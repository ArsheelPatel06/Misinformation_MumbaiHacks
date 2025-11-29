"""
Deepfake detection using AI Vision models and video analysis
Supports images, videos, and audio deepfake detection
"""
import google.generativeai as genai
from openai import OpenAI
import cv2
import numpy as np
from PIL import Image
import json
import os
import asyncio
import tempfile
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI clients
genai.configure(api_key=settings.gemini_api_key)
openai_client = OpenAI(api_key=settings.openai_api_key)


class DeepfakeAnalysisResult:
    """Result of deepfake analysis"""
    def __init__(
        self,
        is_deepfake: bool,
        confidence: float,
        verdict: str,
        reasoning: str,
        artifacts_detected: List[Dict],
        metadata_issues: List[Dict],
        model_name: str
    ):
        self.is_deepfake = is_deepfake
        self.confidence = confidence
        self.verdict = verdict  # 'real', 'fake', 'uncertain'
        self.reasoning = reasoning
        self.artifacts_detected = artifacts_detected
        self.metadata_issues = metadata_issues
        self.model_name = model_name


class ImageDeepfakeDetector:
    """Detect deepfakes in images using AI Vision models"""
    
    DEEPFAKE_ANALYSIS_PROMPT = """You are a forensic image analyst. Your ONLY job is to find FLAWS in this image. Do not praise its quality.

    **STEP-BY-STEP ANALYSIS REQUIRED**:

    1. **HANDS & FINGERS CHECK (CRITICAL)**:
       - Locate every hand in the image.
       - COUNT the fingers on each hand.
       - Check for malformed joints, merging fingers, or impossible grips.
       - **IF YOU SEE >5 FINGERS, <5 FINGERS (without explanation), OR MERGED FINGERS -> MARK AS FAKE IMMEDIATELY.**

    2. **EYES & FACE CHECK**:
       - Zoom in on pupils. Are they perfectly circular?
       - Check reflections in eyes. Do they match?
       - Check teeth. are they individual or a solid white bar?

    3. **PHYSICS CHECK**:
       - Shadows: Do they fall in the correct direction?
       - Reflections: Do they match the object?

    **VERDICT RULES**:
    - Any anatomical error (6 fingers, bad teeth) = **FAKE** (Confidence 1.0).
    - Any strong physics error = **FAKE**.
    - Perfect lighting but "glossy/plastic" skin = **UNCERTAIN** or **FAKE**.
    - Only mark **REAL** if you can find NO flaws after deep scrutiny.

    **RESPONSE FORMAT**:
    {
      "verdict": "fake" | "real" | "uncertain",
      "confidence": <float 0.0-1.0>,
      "is_deepfake": <boolean>,
      "reasoning": "I counted X fingers on the left hand...",
      "artifacts_detected": []
    }"""

    async def analyze_with_gemini(self, image_path: str) -> DeepfakeAnalysisResult:
        """Analyze image using Gemini Vision"""
        try:
            # Use Gemini 2.5 Flash Vision model
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Read image
            from PIL import Image
            img = Image.open(image_path)
            
            response = model.generate_content([
                self.DEEPFAKE_ANALYSIS_PROMPT,
                img
            ])
            
            result_text = response.text
            
            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            return DeepfakeAnalysisResult(
                is_deepfake=result.get('is_deepfake', False),
                confidence=result.get('confidence', 0.5),
                verdict=result.get('verdict', 'uncertain'),
                reasoning=result.get('reasoning', ''),
                artifacts_detected=result.get('artifacts_detected', []),
                metadata_issues=[],
                model_name='gemini-vision'
            )
            
        except Exception as e:
            logger.error(f"Gemini vision analysis error: {e}")
            return DeepfakeAnalysisResult(
                is_deepfake=False,
                confidence=0.0,
                verdict='uncertain',
                reasoning=f"Error during analysis: {str(e)}",
                artifacts_detected=[],
                metadata_issues=[],
                model_name='gemini-vision'
            )
    
    async def analyze_with_openai(self, image_path: str) -> DeepfakeAnalysisResult:
        """Analyze image using OpenAI Vision"""
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                import base64
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.DEEPFAKE_ANALYSIS_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return DeepfakeAnalysisResult(
                is_deepfake=result.get('is_deepfake', False),
                confidence=result.get('confidence', 0.5),
                verdict=result.get('verdict', 'uncertain'),
                reasoning=result.get('reasoning', ''),
                artifacts_detected=result.get('artifacts_detected', []),
                metadata_issues=[],
                model_name='openai-vision'
            )
            
        except Exception as e:
            logger.error(f"OpenAI vision analysis error: {e}")
            return DeepfakeAnalysisResult(
                is_deepfake=False,
                confidence=0.0,
                verdict='uncertain',
                reasoning=f"Error during analysis: {str(e)}",
                artifacts_detected=[],
                metadata_issues=[],
                model_name='openai-vision'
            )
    
    def analyze_metadata(self, image_path: str) -> List[Dict]:
        """Analyze image metadata for manipulation signs"""
        issues = []
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            img = Image.open(image_path)
            
            # Check for EXIF data
            exif_data = img._getexif()
            
            if exif_data is None:
                issues.append({
                    "type": "missing_exif",
                    "description": "No EXIF metadata found - may indicate manipulation",
                    "severity": "medium"
                })
            else:
                # Check for software tags (AI generators often leave traces)
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "Software":
                        software_lower = str(value).lower()
                        ai_keywords = ['midjourney', 'stable diffusion', 'dall-e', 'ai', 'generated']
                        if any(keyword in software_lower for keyword in ai_keywords):
                            issues.append({
                                "type": "ai_software_detected",
                                "description": f"AI generation software detected: {value}",
                                "severity": "high"
                            })
            
            # Check image dimensions (AI generators often use specific sizes)
            width, height = img.size
            common_ai_sizes = [(512, 512), (1024, 1024), (768, 768), (1024, 768)]
            if (width, height) in common_ai_sizes:
                issues.append({
                    "type": "suspicious_dimensions",
                    "description": f"Image size {width}x{height} matches common AI generation dimensions",
                    "severity": "low"
                })
            
        except Exception as e:
            logger.error(f"Metadata analysis error: {e}")
        
        return issues


class VideoDeepfakeDetector:
    """Detect deepfakes in videos"""
    
    def extract_key_frames(self, video_path: str, num_frames: int = 5) -> List[str]:
        """Extract key frames from video for analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Select frames evenly distributed
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            frame_paths = []
            temp_dir = tempfile.mkdtemp()
            
            for idx, frame_num in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                
                if ret:
                    frame_path = os.path.join(temp_dir, f"frame_{idx}.jpg")
                    cv2.imwrite(frame_path, frame)
                    frame_paths.append(frame_path)
            
            cap.release()
            return frame_paths
            
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return []
    
    def check_temporal_consistency(self, video_path: str) -> Dict:
        """Check for temporal inconsistencies in video"""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            inconsistencies = []
            prev_frame = None
            frame_count = 0
            
            while frame_count < 50:  # Analyze first 50 frames (Reduced from 100)
                ret, frame = cap.read()
                if not ret:
                    break
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(frame, prev_frame)
                    diff_score = np.mean(diff)
                    
                    # Sudden large changes might indicate splicing
                    if diff_score > 50:  # Threshold
                        inconsistencies.append({
                            "frame": frame_count,
                            "type": "sudden_change",
                            "score": float(diff_score)
                        })
                
                prev_frame = frame
                frame_count += 1
            
            cap.release()
            
            return {
                "fps": fps,
                "frames_analyzed": frame_count,
                "inconsistencies": inconsistencies,
                "suspicious": len(inconsistencies) > 5
            }
            
        except Exception as e:
            logger.error(f"Temporal consistency check error: {e}")
            return {"error": str(e)}


class DeepfakeDetector:
    """Main deepfake detector coordinating all detection methods"""
    
    def __init__(self):
        self.image_detector = ImageDeepfakeDetector()
        self.video_detector = VideoDeepfakeDetector()
    
    async def analyze_image(self, image_path: str, use_consensus: bool = True) -> Tuple[DeepfakeAnalysisResult, Optional[DeepfakeAnalysisResult]]:
        """
        Analyze an image for deepfake signs
        
        Returns:
            Tuple of (consensus_result, gemini_result) or (gemini_result, None)
        """
        logger.info(f"Analyzing image: {image_path}")
        
        # Metadata analysis
        metadata_issues = self.image_detector.analyze_metadata(image_path)
        
        if use_consensus and settings.enable_consensus_mode:
            # Use both models
            gemini_result = await self.image_detector.analyze_with_gemini(image_path)
            openai_result = await self.image_detector.analyze_with_openai(image_path)
            
            # Add metadata issues to both
            gemini_result.metadata_issues = metadata_issues
            openai_result.metadata_issues = metadata_issues
            
            # Create consensus
            consensus = self._create_consensus(gemini_result, openai_result)
            
            return consensus, gemini_result
        else:
            # Use Gemini only
            result = await self.image_detector.analyze_with_gemini(image_path)
            result.metadata_issues = metadata_issues
            return result, None
    
    async def analyze_video(self, video_path: str) -> Dict:
        """Analyze a video for deepfake signs"""
        logger.info(f"Analyzing video: {video_path}")
        
        # Extract key frames (Reduced to 3 for performance)
        frame_paths = self.video_detector.extract_key_frames(video_path, num_frames=3)
        
        if not frame_paths:
            return {
                "error": "Failed to extract frames from video",
                "is_deepfake": False,
                "confidence": 0.0
            }
        
        # Analyze frames in parallel using asyncio.gather
        tasks = [self.analyze_image(frame_path, use_consensus=False) for frame_path in frame_paths]
        results = await asyncio.gather(*tasks)
        
        frame_results = []
        for result, _ in results:
            frame_results.append({
                "is_deepfake": result.is_deepfake,
                "confidence": result.confidence,
                "verdict": result.verdict
            })
        
        # Check temporal consistency (Reduced to 50 frames in video_detector)
        temporal_analysis = self.video_detector.check_temporal_consistency(video_path)
        
        # Aggregate results
        deepfake_count = sum(1 for r in frame_results if r['is_deepfake'])
        avg_confidence = np.mean([r['confidence'] for r in frame_results]) if frame_results else 0.0
        
        is_deepfake = deepfake_count >= len(frame_results) / 2  # Majority vote
        
        # Clean up temp frames
        for path in frame_paths:
            try:
                os.remove(path)
                os.rmdir(os.path.dirname(path))
            except:
                pass
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": float(avg_confidence),
            "verdict": "fake" if is_deepfake else "real",
            "frame_analysis": frame_results,
            "temporal_analysis": temporal_analysis,
            "frames_analyzed": len(frame_results)
        }
    
    def _create_consensus(
        self,
        gemini: DeepfakeAnalysisResult,
        openai: DeepfakeAnalysisResult
    ) -> DeepfakeAnalysisResult:
        """Create consensus from both models"""
        
        # If both agree
        if gemini.verdict == openai.verdict:
            confidence = max(gemini.confidence, openai.confidence)
            verdict = gemini.verdict
            is_deepfake = gemini.is_deepfake
            reasoning = f"Both models agree: {verdict.upper()}\n\nGemini: {gemini.reasoning}\n\nOpenAI: {openai.reasoning}"
        else:
            # Disagree - use higher confidence
            if gemini.confidence > openai.confidence:
                verdict = gemini.verdict
                is_deepfake = gemini.is_deepfake
                confidence = gemini.confidence * 0.8
            else:
                verdict = openai.verdict
                is_deepfake = openai.is_deepfake
                confidence = openai.confidence * 0.8
            
            reasoning = f"Models disagree (Gemini: {gemini.verdict}, OpenAI: {openai.verdict})\n\nGemini: {gemini.reasoning}\n\nOpenAI: {openai.reasoning}"
        
        # Combine artifacts
        all_artifacts = gemini.artifacts_detected + openai.artifacts_detected
        all_metadata = gemini.metadata_issues + openai.metadata_issues
        
        return DeepfakeAnalysisResult(
            is_deepfake=is_deepfake,
            confidence=confidence,
            verdict=verdict,
            reasoning=reasoning,
            artifacts_detected=all_artifacts,
            metadata_issues=all_metadata,
            model_name='consensus'
        )
