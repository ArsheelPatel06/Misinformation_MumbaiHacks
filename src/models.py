"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SourceCreate(BaseModel):
    """Create a new content source"""
    name: str
    source_type: str  # 'rss', 'news_api', 'reddit', 'twitter'
    url: Optional[str] = None


class SourceResponse(BaseModel):
    """Source response model"""
    id: int
    name: str
    source_type: str
    url: Optional[str]
    is_active: bool
    last_checked: datetime
    
    class Config:
        from_attributes = True


class ClaimResponse(BaseModel):
    """Claim response model"""
    id: int
    text: str
    source_url: Optional[str]
    source_title: Optional[str]
    crisis_type: Optional[str]
    urgency_score: float
    entities: Optional[List]
    topics: Optional[List]
    verification_status: str
    credibility_score: float
    detected_at: datetime
    verified_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VerificationResponse(BaseModel):
    """Verification response model"""
    id: int
    claim_id: int
    model_name: str
    verdict: str
    confidence: float
    supporting_sources: Optional[List]
    contradicting_sources: Optional[List]
    reasoning: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExplanationResponse(BaseModel):
    """Explanation response model"""
    id: int
    claim_id: int
    audience_level: str
    title: str
    summary: str
    detailed_explanation: str
    citations: Optional[List]
    what_to_do: Optional[str]
    what_to_avoid: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClaimDetailResponse(BaseModel):
    """Detailed claim with verification and explanation"""
    claim: ClaimResponse
    verifications: List[VerificationResponse]
    explanations: List[ExplanationResponse]


class VerifyClaimRequest(BaseModel):
    """Request to verify a custom claim"""
    text: str = Field(..., min_length=10, max_length=1000)
    audience_level: str = Field(default="general", pattern="^(simple|general|expert)$")


class TrendingClaimsResponse(BaseModel):
    """Trending misinformation claims"""
    claims: List[ClaimResponse]
    total_count: int
    crisis_breakdown: dict  # Count by crisis type
