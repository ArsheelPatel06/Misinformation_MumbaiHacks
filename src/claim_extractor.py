"""
AI-powered claim extraction using both Gemini and OpenAI
"""
import google.generativeai as genai
from openai import OpenAI
import json
from typing import List, Dict, Optional
from src.config import settings
from src.content_monitor import ContentItem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI clients
genai.configure(api_key=settings.gemini_api_key)
gemini_model = genai.GenerativeModel(settings.gemini_model)
openai_client = OpenAI(api_key=settings.openai_api_key)


class ExtractedClaim:
    """Represents an extracted claim with metadata"""
    def __init__(
        self,
        text: str,
        source_url: str,
        source_title: str,
        crisis_type: str,
        urgency_score: float,
        entities: List[str],
        topics: List[str]
    ):
        self.text = text
        self.source_url = source_url
        self.source_title = source_title
        self.crisis_type = crisis_type
        self.urgency_score = urgency_score
        self.entities = entities
        self.topics = topics


class ClaimExtractor:
    """Extract and analyze claims from content using AI"""
    
    EXTRACTION_PROMPT = """You are an expert fact-checker analyzing content for potential misinformation during global crises.

Analyze the following content and extract factual claims that could be verified or debunked:

Title: {title}
Content: {text}
Source: {source}

Extract claims that are:
1. Factual statements (not opinions)
2. Verifiable or falsifiable
3. Related to crisis events (pandemic, conflict, climate, etc.)
4. Potentially impactful if false

For each claim, provide:
- The exact claim text
- Crisis type (pandemic/conflict/climate/disaster/other)
- Urgency score (0.0-1.0, how urgent is verification)
- Named entities mentioned (people, places, organizations)
- Key topics/keywords

Respond in JSON format:
{{
  "claims": [
    {{
      "text": "exact claim statement",
      "crisis_type": "pandemic",
      "urgency_score": 0.8,
      "entities": ["entity1", "entity2"],
      "topics": ["topic1", "topic2"]
    }}
  ]
}}

If no verifiable claims are found, return empty claims array."""

    async def extract_with_gemini(self, content: ContentItem) -> List[ExtractedClaim]:
        """Extract claims using Gemini"""
        try:
            prompt = self.EXTRACTION_PROMPT.format(
                title=content.title,
                text=content.text[:2000],  # Limit text length
                source=content.source
            )
            
            response = gemini_model.generate_content(prompt)
            result_text = response.text
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            claims = []
            for claim_data in result.get('claims', []):
                claims.append(ExtractedClaim(
                    text=claim_data['text'],
                    source_url=content.url,
                    source_title=content.title,
                    crisis_type=claim_data.get('crisis_type', 'other'),
                    urgency_score=claim_data.get('urgency_score', 0.5),
                    entities=claim_data.get('entities', []),
                    topics=claim_data.get('topics', [])
                ))
            
            return claims
            
        except Exception as e:
            logger.error(f"Gemini extraction error: {e}")
            return []
    
    async def extract_with_openai(self, content: ContentItem) -> List[ExtractedClaim]:
        """Extract claims using OpenAI"""
        try:
            prompt = self.EXTRACTION_PROMPT.format(
                title=content.title,
                text=content.text[:2000],
                source=content.source
            )
            
            response = openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert fact-checker analyzing content for misinformation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            claims = []
            for claim_data in result.get('claims', []):
                claims.append(ExtractedClaim(
                    text=claim_data['text'],
                    source_url=content.url,
                    source_title=content.title,
                    crisis_type=claim_data.get('crisis_type', 'other'),
                    urgency_score=claim_data.get('urgency_score', 0.5),
                    entities=claim_data.get('entities', []),
                    topics=claim_data.get('topics', [])
                ))
            
            return claims
            
        except Exception as e:
            logger.error(f"OpenAI extraction error: {e}")
            return []
    
    async def extract_claims(self, content: ContentItem, use_consensus: bool = False) -> List[ExtractedClaim]:
        """
        Extract claims from content
        
        Args:
            content: Content item to analyze
            use_consensus: If True, use both models and compare results
        """
        if use_consensus and settings.enable_consensus_mode:
            # Use both models for high-urgency content
            gemini_claims = await self.extract_with_gemini(content)
            openai_claims = await self.extract_with_openai(content)
            
            # Merge and deduplicate claims
            all_claims = gemini_claims + openai_claims
            unique_claims = self._deduplicate_claims(all_claims)
            
            logger.info(f"Consensus mode: {len(gemini_claims)} from Gemini, {len(openai_claims)} from OpenAI, {len(unique_claims)} unique")
            return unique_claims
        else:
            # Use Gemini as primary
            return await self.extract_with_gemini(content)
    
    def _deduplicate_claims(self, claims: List[ExtractedClaim]) -> List[ExtractedClaim]:
        """Remove duplicate claims based on text similarity"""
        if not claims:
            return []
        
        unique = []
        seen_texts = set()
        
        for claim in claims:
            # Simple deduplication by normalized text
            normalized = claim.text.lower().strip()
            if normalized not in seen_texts:
                unique.append(claim)
                seen_texts.add(normalized)
        
        return unique
    
    async def batch_extract(self, content_items: List[ContentItem], max_items: int = 50) -> List[ExtractedClaim]:
        """Extract claims from multiple content items"""
        all_claims = []
        
        for i, content in enumerate(content_items[:max_items]):
            logger.info(f"Extracting claims from item {i+1}/{min(len(content_items), max_items)}")
            
            # Use consensus mode for high-priority sources
            use_consensus = i < 5  # Use consensus for first 5 items
            
            claims = await self.extract_claims(content, use_consensus=use_consensus)
            all_claims.extend(claims)
        
        logger.info(f"Total claims extracted: {len(all_claims)}")
        return all_claims
