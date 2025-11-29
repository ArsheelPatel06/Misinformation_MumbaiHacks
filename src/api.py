"""
FastAPI REST API for the misinformation detection agent
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import os
import shutil
from pathlib import Path
from datetime import datetime
from src.database import get_db, init_db, Claim, Verification, Explanation, Media
from src.models import (
    ClaimResponse, VerificationResponse, ExplanationResponse,
    ClaimDetailResponse, VerifyClaimRequest, TrendingClaimsResponse,
    SourceResponse
)
from src.agent import agent
from src.deepfake_detector import DeepfakeDetector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Upload directory for media files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize deepfake detector
deepfake_detector = DeepfakeDetector()

# Initialize FastAPI app
app = FastAPI(
    title="DeepCheck MH - Misinformation Detection API",
    description="AI-powered misinformation detection and verification system",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "DeepCheck MH API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Text claim verification",
            "Deepfake detection (images & videos)",
            "Multi-source content monitoring",
            "Dual-AI verification (OpenAI + Gemini)"
        ],
        "endpoints": {
            "claims": "/api/claims",
            "trending": "/api/trending",
            "verify": "/api/verify",
            "run_cycle": "/api/run-cycle",
            "deepfake_upload": "/api/deepfake/upload",
            "deepfake_analyze": "/api/deepfake/analyze/{media_id}",
            "deepfake_results": "/api/deepfake/results"
        }
    }


@app.get("/api/claims", response_model=List[ClaimResponse])
async def get_claims(
    skip: int = 0,
    limit: int = 50,
    crisis_type: str = None,
    verification_status: str = None,
    db: Session = Depends(get_db)
):
    """Get list of detected claims with optional filtering"""
    query = db.query(Claim)
    
    if crisis_type:
        query = query.filter(Claim.crisis_type == crisis_type)
    
    if verification_status:
        query = query.filter(Claim.verification_status == verification_status)
    
    claims = query.order_by(desc(Claim.detected_at)).offset(skip).limit(limit).all()
    return claims


@app.get("/api/claims/{claim_id}", response_model=ClaimDetailResponse)
async def get_claim_detail(claim_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific claim"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    verifications = db.query(Verification).filter(Verification.claim_id == claim_id).all()
    explanations = db.query(Explanation).filter(Explanation.claim_id == claim_id).all()
    
    return {
        "claim": claim,
        "verifications": verifications,
        "explanations": explanations
    }


@app.get("/api/trending", response_model=TrendingClaimsResponse)
async def get_trending_claims(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get trending misinformation claims"""
    # Get recent claims with high urgency or low credibility
    claims = db.query(Claim).filter(
        (Claim.urgency_score > 0.5) | (Claim.credibility_score < 0.5)
    ).order_by(
        desc(Claim.urgency_score),
        desc(Claim.detected_at)
    ).limit(limit).all()
    
    # Get crisis breakdown
    crisis_breakdown = {}
    crisis_counts = db.query(
        Claim.crisis_type,
        func.count(Claim.id)
    ).group_by(Claim.crisis_type).all()
    
    for crisis_type, count in crisis_counts:
        if crisis_type:
            crisis_breakdown[crisis_type] = count
    
    return {
        "claims": claims,
        "total_count": len(claims),
        "crisis_breakdown": crisis_breakdown
    }


@app.post("/api/verify")
async def verify_custom_claim(
    request: VerifyClaimRequest,
    background_tasks: BackgroundTasks
):
    """Verify a custom claim submitted by user"""
    try:
        result = await agent.verify_custom_claim(
            request.text,
            audience_level=request.audience_level
        )
        return result
    except Exception as e:
        logger.error(f"Error verifying claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run-cycle")
async def run_detection_cycle(background_tasks: BackgroundTasks):
    """Manually trigger a detection cycle"""
    try:
        background_tasks.add_task(agent.run_detection_cycle)
        return {
            "status": "started",
            "message": "Detection cycle started in background"
        }
    except Exception as e:
        logger.error(f"Error starting detection cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_claims = db.query(func.count(Claim.id)).scalar()
    verified_claims = db.query(func.count(Claim.id)).filter(
        Claim.verification_status != 'pending'
    ).scalar()
    
    false_claims = db.query(func.count(Claim.id)).filter(
        Claim.verification_status == 'false'
    ).scalar()
    
    return {
        "total_claims": total_claims,
        "verified_claims": verified_claims,
        "false_claims": false_claims,
        "verification_rate": verified_claims / total_claims if total_claims > 0 else 0
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# DEEPFAKE DETECTION ENDPOINTS
# ============================================================================

@app.post("/api/deepfake/upload")
async def upload_media(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload image or video for deepfake analysis"""
    try:
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.mp4', '.avi', '.mov', '.webm'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Determine file type
        if file_ext in {'.jpg', '.jpeg', '.png'}:
            file_type = 'image'
        elif file_ext in {'.mp4', '.avi', '.mov', '.webm'}:
            file_type = 'video'
        else:
            file_type = 'unknown'
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        # Create database entry
        media = Media(
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_type,
            file_size=file_size,
            user_description=description,
            analysis_status='pending'
        )
        db.add(media)
        db.commit()
        db.refresh(media)
        
        logger.info(f"Media uploaded: {file.filename} (ID: {media.id})")
        
        return {
            "media_id": media.id,
            "filename": file.filename,
            "file_type": file_type,
            "file_size": file_size,
            "status": "uploaded",
            "message": "File uploaded successfully. Use /api/deepfake/analyze/{media_id} to start analysis."
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deepfake/analyze/{media_id}")
async def analyze_media(
    media_id: int,
    background_tasks: BackgroundTasks,
    use_consensus: bool = True,
    db: Session = Depends(get_db)
):
    """Start deepfake analysis on uploaded media"""
    media = db.query(Media).filter(Media.id == media_id).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if media.analysis_status == 'analyzing':
        return {
            "media_id": media_id,
            "status": "already_analyzing",
            "message": "Analysis already in progress"
        }
    
    # Update status
    media.analysis_status = 'analyzing'
    db.commit()
    
    # Start analysis in background
    background_tasks.add_task(
        run_deepfake_analysis,
        media_id,
        media.file_path,
        media.file_type,
        use_consensus
    )
    
    return {
        "media_id": media_id,
        "status": "analyzing",
        "message": "Deepfake analysis started. Check /api/deepfake/results/{media_id} for results."
    }


async def run_deepfake_analysis(
    media_id: int,
    file_path: str,
    file_type: str,
    use_consensus: bool
):
    """Background task to run deepfake analysis"""
    db = next(get_db())
    
    try:
        logger.info(f"Starting deepfake analysis for media {media_id}")
        
        if file_type == 'image':
            # Analyze image
            consensus_result, gemini_result = await deepfake_detector.analyze_image(
                file_path,
                use_consensus=use_consensus
            )
            
            # Update database
            media = db.query(Media).filter(Media.id == media_id).first()
            media.is_deepfake = consensus_result.is_deepfake
            media.deepfake_confidence = consensus_result.confidence
            media.consensus_verdict = consensus_result.verdict
            media.artifacts_detected = consensus_result.artifacts_detected
            media.metadata_analysis = consensus_result.metadata_issues
            media.analysis_report = consensus_result.reasoning
            media.analysis_status = 'completed'
            media.analyzed_at = datetime.utcnow()
            
            if gemini_result:
                media.gemini_verdict = gemini_result.verdict
                media.gemini_confidence = gemini_result.confidence
            
            if use_consensus and consensus_result.model_name == 'consensus':
                # Extract OpenAI results from consensus
                media.openai_verdict = consensus_result.verdict
                media.openai_confidence = consensus_result.confidence
            
            media.technical_details = {
                "model_used": consensus_result.model_name,
                "artifacts_count": len(consensus_result.artifacts_detected),
                "metadata_issues_count": len(consensus_result.metadata_issues)
            }
            
        elif file_type == 'video':
            # Analyze video
            result = await deepfake_detector.analyze_video(file_path)
            
            media = db.query(Media).filter(Media.id == media_id).first()
            media.is_deepfake = result.get('is_deepfake', False)
            media.deepfake_confidence = result.get('confidence', 0.0)
            media.consensus_verdict = result.get('verdict', 'uncertain')
            media.frame_analysis = result.get('frame_analysis', [])
            media.analysis_report = f"Video analysis: {result.get('frames_analyzed', 0)} frames analyzed"
            media.analysis_status = 'completed'
            media.analyzed_at = datetime.utcnow()
            media.technical_details = result.get('temporal_analysis', {})
        
        db.commit()
        logger.info(f"Deepfake analysis completed for media {media_id}")
        
    except Exception as e:
        logger.error(f"Analysis error for media {media_id}: {e}")
        media = db.query(Media).filter(Media.id == media_id).first()
        if media:
            media.analysis_status = 'failed'
            media.analysis_report = f"Analysis failed: {str(e)}"
            db.commit()
    finally:
        db.close()


@app.get("/api/deepfake/results/{media_id}")
async def get_deepfake_results(media_id: int, db: Session = Depends(get_db)):
    """Get deepfake analysis results for a specific media"""
    media = db.query(Media).filter(Media.id == media_id).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return {
        "media_id": media.id,
        "filename": media.filename,
        "file_type": media.file_type,
        "analysis_status": media.analysis_status,
        "is_deepfake": media.is_deepfake,
        "confidence": media.deepfake_confidence,
        "verdict": media.consensus_verdict,
        "gemini_verdict": media.gemini_verdict,
        "gemini_confidence": media.gemini_confidence,
        "openai_verdict": media.openai_verdict,
        "openai_confidence": media.openai_confidence,
        "artifacts_detected": media.artifacts_detected,
        "metadata_analysis": media.metadata_analysis,
        "frame_analysis": media.frame_analysis,
        "analysis_report": media.analysis_report,
        "technical_details": media.technical_details,
        "uploaded_at": media.uploaded_at,
        "analyzed_at": media.analyzed_at,
        "user_description": media.user_description
    }


@app.get("/api/deepfake/results")
async def get_all_deepfake_results(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all deepfake analysis results"""
    query = db.query(Media)
    
    if status:
        query = query.filter(Media.analysis_status == status)
    
    media_list = query.order_by(desc(Media.uploaded_at)).offset(skip).limit(limit).all()
    
    return {
        "total": len(media_list),
        "results": [
            {
                "media_id": m.id,
                "filename": m.filename,
                "file_type": m.file_type,
                "analysis_status": m.analysis_status,
                "is_deepfake": m.is_deepfake,
                "confidence": m.deepfake_confidence,
                "verdict": m.consensus_verdict,
                "uploaded_at": m.uploaded_at,
                "analyzed_at": m.analyzed_at
            }
            for m in media_list
        ]
    }


if __name__ == "__main__":
    import uvicorn
    from src.config import settings
    
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
