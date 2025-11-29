# Deepfake Detection Guide

## Overview

DeepCheck MH now includes **comprehensive deepfake detection** for images and videos using dual-AI verification with both **Gemini Vision** and **OpenAI Vision** APIs.

## Features

### Image Deepfake Detection
- **Dual-AI Analysis**: Uses both Gemini Vision and OpenAI Vision
- **Consensus Mode**: Cross-validates results from both models
- **Artifact Detection**: Identifies visual inconsistencies, unnatural textures, lighting issues
- **Metadata Analysis**: Checks EXIF data for manipulation signs
- **AI Generation Detection**: Identifies traces of AI generation software

### Video Deepfake Detection
- **Frame Extraction**: Analyzes key frames from videos
- **Temporal Consistency**: Checks for frame-to-frame inconsistencies
- **Multi-Frame Analysis**: Aggregates results across multiple frames
- **Splicing Detection**: Identifies sudden changes indicating manipulation

## How It Works

### Detection Process

1. **Upload Media** → File is saved and database entry created
2. **Metadata Analysis** → EXIF data checked for manipulation signs
3. **Visual Analysis** → Both AI models analyze the image/video
4. **Artifact Detection** → Identifies specific manipulation artifacts
5. **Consensus** → Results from both models are compared
6. **Report Generation** → Detailed analysis report created

### What We Detect

#### Facial Deepfakes
- Unnatural skin texture or lighting
- Inconsistent shadows or reflections
- Odd eye alignment or blinking patterns
- Teeth or facial feature irregularities
- Hair-face boundary artifacts

#### AI-Generated Images
- Blurring or smudging in backgrounds
- Repetitive patterns or textures
- Inconsistent perspective or geometry
- Unnatural color gradients
- Missing or distorted fine details

#### Manipulation Signs
- Cloning or copy-paste artifacts
- Edge inconsistencies
- Lighting direction mismatches
- Resolution inconsistencies

## API Usage

### 1. Upload Media

```bash
curl -X POST "http://localhost:8000/api/deepfake/upload" \
  -F "file=@suspicious_image.jpg" \
  -F "description=Image from social media claiming to show XYZ"
```

**Response:**
```json
{
  "media_id": 1,
  "filename": "suspicious_image.jpg",
  "file_type": "image",
  "file_size": 245678,
  "status": "uploaded",
  "message": "File uploaded successfully. Use /api/deepfake/analyze/1 to start analysis."
}
```

### 2. Start Analysis

```bash
curl -X POST "http://localhost:8000/api/deepfake/analyze/1?use_consensus=true"
```

**Response:**
```json
{
  "media_id": 1,
  "status": "analyzing",
  "message": "Deepfake analysis started. Check /api/deepfake/results/1 for results."
}
```

### 3. Get Results

```bash
curl "http://localhost:8000/api/deepfake/results/1"
```

**Response:**
```json
{
  "media_id": 1,
  "filename": "suspicious_image.jpg",
  "file_type": "image",
  "analysis_status": "completed",
  "is_deepfake": true,
  "confidence": 0.87,
  "verdict": "fake",
  "gemini_verdict": "fake",
  "gemini_confidence": 0.85,
  "openai_verdict": "fake",
  "openai_confidence": 0.89,
  "artifacts_detected": [
    {
      "type": "facial_inconsistency",
      "description": "Unnatural skin texture around eyes",
      "severity": "high"
    },
    {
      "type": "ai_artifact",
      "description": "Repetitive background patterns typical of AI generation",
      "severity": "medium"
    }
  ],
  "metadata_analysis": [
    {
      "type": "missing_exif",
      "description": "No EXIF metadata found - may indicate manipulation",
      "severity": "medium"
    }
  ],
  "analysis_report": "Both models agree: FAKE\n\nGemini: This image shows clear signs of AI generation...",
  "uploaded_at": "2025-11-29T03:45:00",
  "analyzed_at": "2025-11-29T03:45:15"
}
```

### 4. List All Analyses

```bash
curl "http://localhost:8000/api/deepfake/results?limit=10"
```

## Supported File Types

### Images
- `.jpg`, `.jpeg`
- `.png`

### Videos
- `.mp4`
- `.avi`
- `.mov`
- `.webm`

## Interpretation Guide

### Verdict Types
- **`real`**: High confidence the media is authentic
- **`fake`**: High confidence the media is manipulated/AI-generated
- **`uncertain`**: Insufficient evidence to make determination

### Confidence Scores
- **0.9 - 1.0**: Very high confidence
- **0.7 - 0.9**: High confidence
- **0.5 - 0.7**: Moderate confidence
- **0.0 - 0.5**: Low confidence

### Consensus Mode
When `use_consensus=true`:
- Both Gemini and OpenAI analyze the media
- If they agree → confidence is boosted
- If they disagree → confidence is reduced, higher-confidence model is used
- Results from both models are saved for transparency

## Example Workflow

### Scenario: Verify Suspicious Social Media Image

1. **Download the image** from social media
2. **Upload to DeepCheck**:
   ```bash
   curl -X POST "http://localhost:8000/api/deepfake/upload" \
     -F "file=@downloaded_image.jpg" \
     -F "description=Viral image claiming to show disaster"
   ```

3. **Start analysis** with consensus mode:
   ```bash
   curl -X POST "http://localhost:8000/api/deepfake/analyze/1?use_consensus=true"
   ```

4. **Wait 10-30 seconds** for analysis to complete

5. **Get results**:
   ```bash
   curl "http://localhost:8000/api/deepfake/results/1"
   ```

6. **Review the report**:
   - Check `is_deepfake` and `confidence`
   - Read `analysis_report` for detailed explanation
   - Review `artifacts_detected` for specific issues
   - Check if both models agree (consensus)

## Technical Details

### Image Analysis
- Uses Gemini 1.5 Flash Vision and GPT-4o-mini Vision
- Analyzes facial features, textures, lighting, and artifacts
- Checks metadata (EXIF) for manipulation signs
- Identifies AI generation software traces

### Video Analysis
- Extracts 5 key frames evenly distributed
- Analyzes each frame independently
- Checks temporal consistency between frames
- Uses majority voting for final verdict
- Detects sudden changes indicating splicing

### Metadata Analysis
- Checks for missing EXIF data
- Identifies AI generation software signatures
- Detects suspicious image dimensions
- Analyzes modification timestamps

## Best Practices

1. **Use Consensus Mode** for important verifications
2. **Review Both Models** when they disagree
3. **Check Artifacts** for specific manipulation signs
4. **Consider Context** - technical analysis + human judgment
5. **Verify Sources** - cross-reference with other evidence

## Limitations

- **Not 100% Accurate**: AI detection is probabilistic
- **Evolving Techniques**: New deepfake methods emerge constantly
- **Context Needed**: Technical analysis should be combined with source verification
- **File Size Limits**: Large videos may take longer to process

## Testing

Run the deepfake detection test:
```bash
python test_deepfake.py
```

This will verify:
- ✓ API keys configured
- ✓ Database initialized with Media table
- ✓ Deepfake detection endpoints available

## Integration with Frontend

The frontend can:
1. Provide drag-and-drop upload interface
2. Show real-time analysis progress
3. Display results with visual indicators
4. Highlight detected artifacts on the image
5. Show comparison between Gemini and OpenAI results
6. Provide shareable reports

---

**Deepfake detection is now fully integrated into DeepCheck MH!** 🎉

The system can detect manipulated images and videos using state-of-the-art AI vision models with dual verification for maximum accuracy.
