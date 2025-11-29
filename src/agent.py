"""
Main AI Agent orchestrator
Coordinates content monitoring, claim extraction, verification, and explanation generation
"""
import asyncio
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from src.content_monitor import ContentAggregator, ContentItem
from src.claim_extractor import ClaimExtractor, ExtractedClaim
from src.fact_checker import FactChecker, VerificationResult
from src.explanation_generator import ExplanationGenerator, Explanation
from src.database import SessionLocal, Claim, Verification, Explanation as DBExplanation, init_db
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MisinfoAgent:
    """Main AI agent for misinformation detection and verification"""
    
    def __init__(self):
        self.content_aggregator = ContentAggregator()
        self.claim_extractor = ClaimExtractor()
        self.fact_checker = FactChecker()
        self.explanation_generator = ExplanationGenerator()
        self.is_running = False
    
    async def run_detection_cycle(self) -> dict:
        """Run a complete detection and verification cycle"""
        logger.info("=" * 60)
        logger.info("Starting misinformation detection cycle")
        logger.info("=" * 60)
        
        stats = {
            'content_items': 0,
            'claims_extracted': 0,
            'claims_verified': 0,
            'explanations_generated': 0,
            'start_time': datetime.utcnow()
        }
        
        try:
            # Step 1: Fetch content from all sources
            logger.info("Step 1: Fetching content from all sources...")
            content_items = await self.content_aggregator.fetch_all_content()
            stats['content_items'] = len(content_items)
            
            if not content_items:
                logger.warning("No content items found")
                return stats
            
            # Step 2: Extract claims from content
            logger.info(f"Step 2: Extracting claims from {len(content_items)} content items...")
            extracted_claims = await self.claim_extractor.batch_extract(
                content_items,
                max_items=settings.max_claims_per_cycle
            )
            stats['claims_extracted'] = len(extracted_claims)
            
            if not extracted_claims:
                logger.warning("No claims extracted")
                return stats
            
            # Step 3: Verify claims and generate explanations
            logger.info(f"Step 3: Verifying {len(extracted_claims)} claims...")
            db = SessionLocal()
            
            try:
                for i, claim in enumerate(extracted_claims):
                    logger.info(f"Processing claim {i+1}/{len(extracted_claims)}: {claim.text[:100]}...")
                    
                    # Verify claim
                    primary_verification, secondary_verification = await self.fact_checker.verify_claim(
                        claim,
                        use_consensus=True
                    )
                    
                    # Calculate credibility score
                    credibility_score = self.fact_checker.calculate_credibility_score(primary_verification)
                    
                    # Save claim to database
                    db_claim = Claim(
                        text=claim.text,
                        source_url=claim.source_url,
                        source_title=claim.source_title,
                        crisis_type=claim.crisis_type,
                        urgency_score=claim.urgency_score,
                        entities=claim.entities,
                        topics=claim.topics,
                        verification_status=primary_verification.verdict,
                        credibility_score=credibility_score,
                        verified_at=datetime.utcnow()
                    )
                    db.add(db_claim)
                    db.flush()  # Get the claim ID
                    
                    # Save primary verification
                    db_verification = Verification(
                        claim_id=db_claim.id,
                        model_name=primary_verification.model_name,
                        verdict=primary_verification.verdict,
                        confidence=primary_verification.confidence,
                        reasoning=primary_verification.reasoning,
                        supporting_sources=primary_verification.supporting_sources,
                        contradicting_sources=primary_verification.contradicting_sources
                    )
                    db.add(db_verification)
                    db.flush()
                    
                    # Save secondary verification if exists
                    if secondary_verification:
                        db_verification_2 = Verification(
                            claim_id=db_claim.id,
                            model_name=secondary_verification.model_name,
                            verdict=secondary_verification.verdict,
                            confidence=secondary_verification.confidence,
                            reasoning=secondary_verification.reasoning,
                            supporting_sources=secondary_verification.supporting_sources,
                            contradicting_sources=secondary_verification.contradicting_sources
                        )
                        db.add(db_verification_2)
                    
                    # Generate explanation (general audience by default)
                    explanation = await self.explanation_generator.generate_explanation(
                        claim,
                        primary_verification,
                        audience_level='general'
                    )
                    
                    # Save explanation
                    db_explanation = DBExplanation(
                        claim_id=db_claim.id,
                        verification_id=db_verification.id,
                        audience_level=explanation.audience_level,
                        title=explanation.title,
                        summary=explanation.summary,
                        detailed_explanation=explanation.detailed_explanation,
                        citations=explanation.citations,
                        what_to_do=explanation.what_to_do,
                        what_to_avoid=explanation.what_to_avoid
                    )
                    db.add(db_explanation)
                    
                    stats['claims_verified'] += 1
                    stats['explanations_generated'] += 1
                
                db.commit()
                logger.info("All claims saved to database")
                
            except Exception as e:
                logger.error(f"Error during claim processing: {e}")
                db.rollback()
                raise
            finally:
                db.close()
            
            stats['end_time'] = datetime.utcnow()
            stats['duration_seconds'] = (stats['end_time'] - stats['start_time']).total_seconds()
            
            logger.info("=" * 60)
            logger.info("Detection cycle completed")
            logger.info(f"Content items: {stats['content_items']}")
            logger.info(f"Claims extracted: {stats['claims_extracted']}")
            logger.info(f"Claims verified: {stats['claims_verified']}")
            logger.info(f"Duration: {stats['duration_seconds']:.1f}s")
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in detection cycle: {e}")
            raise
    
    async def verify_custom_claim(self, claim_text: str, audience_level: str = 'general') -> dict:
        """Verify a custom claim submitted by a user"""
        logger.info(f"Verifying custom claim: {claim_text}")
        
        # Create a minimal ExtractedClaim object
        claim = ExtractedClaim(
            text=claim_text,
            source_url="user_submitted",
            source_title="User Submitted Claim",
            crisis_type="general",
            urgency_score=0.7,
            entities=[],
            topics=[]
        )
        
        # Verify with consensus mode
        primary_verification, secondary_verification = await self.fact_checker.verify_claim(
            claim,
            use_consensus=True
        )
        
        # Generate explanation
        explanation = await self.explanation_generator.generate_explanation(
            claim,
            primary_verification,
            audience_level=audience_level
        )
        
        # Calculate credibility
        credibility_score = self.fact_checker.calculate_credibility_score(primary_verification)
        
        # Save to database
        db = SessionLocal()
        try:
            db_claim = Claim(
                text=claim_text,
                source_url="user_submitted",
                source_title="User Submitted",
                crisis_type="general",
                urgency_score=0.7,
                verification_status=primary_verification.verdict,
                credibility_score=credibility_score,
                verified_at=datetime.utcnow()
            )
            db.add(db_claim)
            db.flush()
            
            db_verification = Verification(
                claim_id=db_claim.id,
                model_name=primary_verification.model_name,
                verdict=primary_verification.verdict,
                confidence=primary_verification.confidence,
                reasoning=primary_verification.reasoning,
                supporting_sources=primary_verification.supporting_sources,
                contradicting_sources=primary_verification.contradicting_sources
            )
            db.add(db_verification)
            db.flush()
            
            db_explanation = DBExplanation(
                claim_id=db_claim.id,
                verification_id=db_verification.id,
                audience_level=explanation.audience_level,
                title=explanation.title,
                summary=explanation.summary,
                detailed_explanation=explanation.detailed_explanation,
                citations=explanation.citations,
                what_to_do=explanation.what_to_do,
                what_to_avoid=explanation.what_to_avoid
            )
            db.add(db_explanation)
            
            db.commit()
            
            return {
                'claim_id': db_claim.id,
                'verdict': primary_verification.verdict,
                'confidence': primary_verification.confidence,
                'credibility_score': credibility_score,
                'explanation': {
                    'title': explanation.title,
                    'summary': explanation.summary,
                    'detailed': explanation.detailed_explanation,
                    'what_to_do': explanation.what_to_do,
                    'what_to_avoid': explanation.what_to_avoid
                }
            }
            
        finally:
            db.close()
    
    async def start_monitoring(self):
        """Start continuous monitoring (background task)"""
        self.is_running = True
        logger.info("Starting continuous monitoring...")
        
        while self.is_running:
            try:
                await self.run_detection_cycle()
                
                # Wait before next cycle
                logger.info(f"Waiting {settings.monitoring_interval} seconds before next cycle...")
                await asyncio.sleep(settings.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_running = False
        logger.info("Stopping monitoring...")


# Global agent instance
agent = MisinfoAgent()
