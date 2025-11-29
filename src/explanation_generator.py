"""
Generate accessible explanations for different audiences
"""
import google.generativeai as genai
from openai import OpenAI
import json
from typing import Dict, List
from src.config import settings
from src.claim_extractor import ExtractedClaim
from src.fact_checker import VerificationResult
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI clients
genai.configure(api_key=settings.gemini_api_key)
gemini_model = genai.GenerativeModel(settings.gemini_model)
openai_client = OpenAI(api_key=settings.openai_api_key)


class Explanation:
    """Represents a generated explanation"""
    def __init__(
        self,
        title: str,
        summary: str,
        detailed_explanation: str,
        citations: List[Dict],
        what_to_do: str,
        what_to_avoid: str,
        audience_level: str
    ):
        self.title = title
        self.summary = summary
        self.detailed_explanation = detailed_explanation
        self.citations = citations
        self.what_to_do = what_to_do
        self.what_to_avoid = what_to_avoid
        self.audience_level = audience_level


class ExplanationGenerator:
    """Generate context-aware explanations for claims"""
    
    EXPLANATION_PROMPTS = {
        'simple': """You are explaining a fact-check result to a general audience with simple, clear language.

CLAIM: {claim}
VERDICT: {verdict}
CONFIDENCE: {confidence}
REASONING: {reasoning}

Create an explanation that:
1. Uses simple, everyday language (8th grade reading level)
2. Avoids jargon and technical terms
3. Provides clear, actionable guidance
4. Is empathetic and non-judgmental

Respond in JSON format:
{{
  "title": "Clear, engaging title",
  "summary": "2-3 sentence summary of the verdict",
  "detailed_explanation": "Full explanation in simple terms",
  "what_to_do": "Practical advice on what to do with this information",
  "what_to_avoid": "What NOT to do or believe",
  "key_points": ["point 1", "point 2", "point 3"]
}}""",
        
        'general': """You are explaining a fact-check result to an informed general audience.

CLAIM: {claim}
VERDICT: {verdict}
CONFIDENCE: {confidence}
REASONING: {reasoning}
CRISIS CONTEXT: {crisis_type}

Create an explanation that:
1. Balances accessibility with detail
2. Provides context about the crisis situation
3. Cites evidence and reasoning
4. Offers actionable guidance

Respond in JSON format:
{{
  "title": "Informative title",
  "summary": "3-4 sentence summary with key context",
  "detailed_explanation": "Comprehensive explanation with evidence",
  "what_to_do": "Recommended actions based on this information",
  "what_to_avoid": "Common misconceptions or harmful actions to avoid",
  "key_points": ["point 1", "point 2", "point 3"]
}}""",
        
        'expert': """You are explaining a fact-check result to experts, researchers, or policymakers.

CLAIM: {claim}
VERDICT: {verdict}
CONFIDENCE: {confidence}
REASONING: {reasoning}
CRISIS CONTEXT: {crisis_type}
ENTITIES: {entities}

Create an explanation that:
1. Provides technical depth and nuance
2. Discusses methodology and confidence levels
3. References specific evidence and sources
4. Addresses implications and limitations

Respond in JSON format:
{{
  "title": "Technical title",
  "summary": "Concise technical summary",
  "detailed_explanation": "In-depth analysis with methodological details",
  "what_to_do": "Expert recommendations and further research needs",
  "what_to_avoid": "Analytical pitfalls and limitations to consider",
  "key_points": ["point 1", "point 2", "point 3"]
}}"""
    }
    
    async def generate_explanation(
        self,
        claim: ExtractedClaim,
        verification: VerificationResult,
        audience_level: str = 'general'
    ) -> Explanation:
        """Generate an explanation tailored to the audience level"""
        
        if audience_level not in self.EXPLANATION_PROMPTS:
            audience_level = 'general'
        
        try:
            prompt = self.EXPLANATION_PROMPTS[audience_level].format(
                claim=claim.text,
                verdict=verification.verdict.upper(),
                confidence=f"{verification.confidence:.0%}",
                reasoning=verification.reasoning,
                crisis_type=claim.crisis_type,
                entities=", ".join(claim.entities) if claim.entities else "None"
            )
            
            # Use Gemini for explanation generation
            response = gemini_model.generate_content(prompt)
            result_text = response.text
            
            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            # Create citations from verification sources
            citations = []
            for source in verification.supporting_sources[:3]:  # Top 3 sources
                citations.append({
                    "text": source.get('text', ''),
                    "source": source.get('source', 'AI Analysis'),
                    "type": "supporting"
                })
            
            return Explanation(
                title=result.get('title', 'Fact Check Result'),
                summary=result.get('summary', ''),
                detailed_explanation=result.get('detailed_explanation', ''),
                citations=citations,
                what_to_do=result.get('what_to_do', ''),
                what_to_avoid=result.get('what_to_avoid', ''),
                audience_level=audience_level
            )
            
        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            
            # Fallback explanation
            return Explanation(
                title=f"Claim Verification: {verification.verdict.upper()}",
                summary=f"This claim has been assessed as {verification.verdict} with {verification.confidence:.0%} confidence.",
                detailed_explanation=verification.reasoning,
                citations=[],
                what_to_do="Verify information from multiple credible sources before sharing.",
                what_to_avoid="Avoid sharing unverified claims during crisis situations.",
                audience_level=audience_level
            )
    
    async def generate_multi_audience_explanations(
        self,
        claim: ExtractedClaim,
        verification: VerificationResult
    ) -> Dict[str, Explanation]:
        """Generate explanations for all audience levels"""
        
        explanations = {}
        
        for level in ['simple', 'general', 'expert']:
            explanation = await self.generate_explanation(claim, verification, level)
            explanations[level] = explanation
        
        return explanations
