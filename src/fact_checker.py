"""
Fact-checking and verification system using dual AI models
"""
import google.generativeai as genai
from openai import OpenAI
import json
import aiohttp
from typing import List, Dict, Optional, Tuple
from src.config import settings
from src.claim_extractor import ExtractedClaim
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI clients
genai.configure(api_key=settings.gemini_api_key)
gemini_model = genai.GenerativeModel(settings.gemini_model)
openai_client = OpenAI(api_key=settings.openai_api_key)


class VerificationResult:
    """Represents a fact-check verification result"""
    def __init__(
        self,
        verdict: str,  # 'true', 'false', 'mixed', 'unverifiable'
        confidence: float,  # 0.0-1.0
        reasoning: str,
        supporting_sources: List[Dict],
        contradicting_sources: List[Dict],
        model_name: str
    ):
        self.verdict = verdict
        self.confidence = confidence
        self.reasoning = reasoning
        self.supporting_sources = supporting_sources
        self.contradicting_sources = contradicting_sources
        self.model_name = model_name


class FactChecker:
    """Verify claims using AI models and external sources"""
    
    VERIFICATION_PROMPT = """You are an expert fact-checker verifying claims during global crises.

Analyze this claim and determine its veracity:

CLAIM: {claim}

Context:
- Crisis Type: {crisis_type}
- Source: {source}
- Entities: {entities}

Your task:
1. Assess if the claim is TRUE, FALSE, MIXED (partially true), or UNVERIFIABLE
2. Provide confidence score (0.0-1.0)
3. Explain your reasoning with specific evidence
4. Identify what sources would support or contradict this claim

Consider:
- Is this claim factually accurate?
- Are there credible sources that verify or contradict it?
- Is the claim taken out of context?
- Are there any logical fallacies or misleading elements?

Respond in JSON format:
{{
  "verdict": "true|false|mixed|unverifiable",
  "confidence": 0.85,
  "reasoning": "detailed explanation of your assessment",
  "supporting_evidence": ["evidence point 1", "evidence point 2"],
  "contradicting_evidence": ["contradiction 1", "contradiction 2"],
  "recommended_sources": ["source type 1", "source type 2"]
}}"""

    async def verify_with_gemini(self, claim: ExtractedClaim) -> VerificationResult:
        """Verify claim using Gemini"""
        try:
            prompt = self.VERIFICATION_PROMPT.format(
                claim=claim.text,
                crisis_type=claim.crisis_type,
                source=claim.source_title,
                entities=", ".join(claim.entities) if claim.entities else "None"
            )
            
            response = gemini_model.generate_content(prompt)
            result_text = response.text
            
            # Parse JSON response
            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            try:
                # Clean up response text
                text = result_text.strip()
                print(f"DEBUG: Cleaned JSON text: {text}")
                
                result = json.loads(text)
                print(f"DEBUG: Parsed JSON: {result}")
                
                # Convert evidence to source format as expected by VerificationResult
                supporting = [{"text": ev, "source": "AI Analysis"} for ev in result.get('supporting_evidence', [])]
                contradicting = [{"text": ev, "source": "AI Analysis"} for ev in result.get('contradicting_evidence', [])]
                
                return VerificationResult(
                    verdict=result.get('verdict', 'unverifiable'),
                    confidence=result.get('confidence', 0.0),
                    reasoning=result.get('reasoning', 'No reasoning provided'),
                    supporting_sources=supporting,
                    contradicting_sources=contradicting,
                    model_name='gemini'
                )
            except Exception as e:
                print(f"DEBUG: Error parsing Gemini response: {e}")
                import traceback
                traceback.print_exc()
                logger.error(f"Error parsing Gemini response: {e}")
                logger.error(f"Raw response: {response.text}")
                return VerificationResult(
                    verdict='unverifiable',
                    confidence=0.0,
                    reasoning=f"Error during verification: {str(e)}",
                    supporting_sources=[],
                    contradicting_sources=[],
                    model_name='gemini'
                )
            
        except Exception as e:
            logger.error(f"Gemini verification error: {e}")
            return VerificationResult(
                verdict='unverifiable',
                confidence=0.0,
                reasoning=f"Error during verification: {str(e)}",
                supporting_sources=[],
                contradicting_sources=[],
                model_name='gemini'
            )
    
    async def verify_with_openai(self, claim: ExtractedClaim) -> VerificationResult:
        """Verify claim using OpenAI"""
        try:
            prompt = self.VERIFICATION_PROMPT.format(
                claim=claim.text,
                crisis_type=claim.crisis_type,
                source=claim.source_title,
                entities=", ".join(claim.entities) if claim.entities else "None"
            )
            
            response = openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert fact-checker with deep knowledge of current events and crisis situations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            supporting = [{"text": ev, "source": "AI Analysis"} for ev in result.get('supporting_evidence', [])]
            contradicting = [{"text": ev, "source": "AI Analysis"} for ev in result.get('contradicting_evidence', [])]
            
            return VerificationResult(
                verdict=result.get('verdict', 'unverifiable'),
                confidence=result.get('confidence', 0.5),
                reasoning=result.get('reasoning', ''),
                supporting_sources=supporting,
                contradicting_sources=contradicting,
                model_name='openai'
            )
            
        except Exception as e:
            logger.error(f"OpenAI verification error: {e}")
            return VerificationResult(
                verdict='unverifiable',
                confidence=0.0,
                reasoning=f"Error during verification: {str(e)}",
                supporting_sources=[],
                contradicting_sources=[],
                model_name='openai'
            )
    
    async def verify_claim(self, claim: ExtractedClaim, use_consensus: bool = True) -> Tuple[VerificationResult, Optional[VerificationResult]]:
        """
        Verify a claim using AI models
        
        Returns:
            Tuple of (primary_result, consensus_result)
            consensus_result is None if consensus mode is disabled
        """
        if use_consensus and settings.enable_consensus_mode and claim.urgency_score > 0.6:
            # High urgency - use both models
            logger.info(f"Using consensus mode for high-urgency claim (score: {claim.urgency_score})")
            
            gemini_result = await self.verify_with_gemini(claim)
            openai_result = await self.verify_with_openai(claim)
            
            # Create consensus result
            consensus = self._create_consensus(gemini_result, openai_result, claim)
            
            return consensus, gemini_result
        else:
            # Normal priority - use Gemini only
            result = await self.verify_with_gemini(claim)
            return result, None
    
    def _create_consensus(self, gemini: VerificationResult, openai: VerificationResult, claim: ExtractedClaim) -> VerificationResult:
        """Create consensus verification from both models"""
        
        # If both agree on verdict, use higher confidence
        if gemini.verdict == openai.verdict:
            confidence = max(gemini.confidence, openai.confidence)
            verdict = gemini.verdict
            reasoning = f"Both models agree: {gemini.verdict.upper()}\n\nGemini: {gemini.reasoning}\n\nOpenAI: {openai.reasoning}"
        else:
            # Models disagree - mark as mixed or use higher confidence
            if gemini.confidence > openai.confidence:
                verdict = gemini.verdict
                confidence = gemini.confidence * 0.8  # Reduce confidence due to disagreement
            else:
                verdict = openai.verdict
                confidence = openai.confidence * 0.8
            
            reasoning = f"Models disagree (Gemini: {gemini.verdict}, OpenAI: {openai.verdict})\n\nGemini: {gemini.reasoning}\n\nOpenAI: {openai.reasoning}"
        
        # Combine sources
        all_supporting = gemini.supporting_sources + openai.supporting_sources
        all_contradicting = gemini.contradicting_sources + openai.contradicting_sources
        
        return VerificationResult(
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            supporting_sources=all_supporting,
            contradicting_sources=all_contradicting,
            model_name='consensus'
        )
    
    def calculate_credibility_score(self, verification: VerificationResult) -> float:
        """Calculate overall credibility score for a claim"""
        
        # Base score on verdict
        verdict_scores = {
            'true': 0.9,
            'false': 0.1,
            'mixed': 0.5,
            'unverifiable': 0.3
        }
        
        base_score = verdict_scores.get(verification.verdict, 0.5)
        
        # Adjust by confidence
        credibility = base_score * verification.confidence
        
        # Adjust by evidence balance
        supporting_count = len(verification.supporting_sources)
        contradicting_count = len(verification.contradicting_sources)
        
        if supporting_count + contradicting_count > 0:
            evidence_ratio = supporting_count / (supporting_count + contradicting_count)
            credibility = (credibility + evidence_ratio) / 2
        
        return round(credibility, 2)
