"""
Process Video API Endpoint
Handles video upload, pose extraction, and embedding generation.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
import os
import shutil

from app.schemas.pose import ProcessVideoResponse
from app.core.pose_model import extract_keypoints
from app.core.embedding import sequence_to_embedding
from app.db.storage import get_storage
from app.db.vector_db import get_vector_db


router = APIRouter()


UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/process-video", response_model=ProcessVideoResponse)
async def process_video(
    video: UploadFile = File(..., description="Video file to process")
):
    """
    Process uploaded video to extract pose keypoints and generate embeddings.
    
    Steps:
    1. Save uploaded video temporarily
    2. Extract pose keypoints using MediaPipe
    3. Generate fixed-length embedding
    4. Store in both JSON storage and vector database
    5. Return session data
    
    Args:
        video: Uploaded video file
        
    Returns:
        ProcessVideoResponse with session_id, keypoints, embedding, and metadata
    """
    # Validate file type
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    file_ext = os.path.splitext(video.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{video.filename}"
    video_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        # Save uploaded file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Extract keypoints
        keypoints, duration_seconds = extract_keypoints(video_path)
        
        if not keypoints or len(keypoints) == 0:
            raise HTTPException(
                status_code=400,
                detail="No pose detected in video. Please ensure a person is visible."
            )
        
        # Generate embedding
        embedding = sequence_to_embedding(keypoints)
        
        # Store in JSON storage
        storage = get_storage()
        session_id = storage.create_session(
            keypoints=keypoints,
            embedding=embedding,
            duration_seconds=duration_seconds,
            video_path=video_path,
            user_id=None  # TODO: Add user authentication
        )
        
        # Store in vector database
        vector_db = get_vector_db()
        vector_db.insert_embedding(
            session_id=session_id,
            embedding=embedding,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "duration_seconds": duration_seconds,
                "video_filename": video.filename
            }
        )
        
        # Return response
        return ProcessVideoResponse(
            session_id=session_id,
            keypoints=keypoints,
            embedding=embedding,
            step_segments=None,  # Placeholder
            duration_seconds=duration_seconds
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up video file on error
        if os.path.exists(video_path):
            os.remove(video_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )
    finally:
        # Close the uploaded file
        await video.close()
