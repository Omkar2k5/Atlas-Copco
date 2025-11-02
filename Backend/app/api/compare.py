"""
Compare API Endpoint
Compares two pose execution sessions and provides metrics.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.compare import CompareRequest, CompareResponse
from app.db.storage import get_storage
from app.core.embedding import cosine_similarity
from app.core.metrics import (
    calculate_movement_deviation,
    calculate_stressed_joints_ergonomic,
    generate_recommendations
)


router = APIRouter()


@router.post("/compare", response_model=CompareResponse)
async def compare_sessions(request: CompareRequest):
    """
    Compare two pose execution sessions.
    
    Analyzes:
    - Movement similarity (embedding cosine similarity)
    - Time difference
    - Per-joint movement deviations
    - Stressed/strained joints
    - Actionable improvement recommendations
    
    Args:
        request: CompareRequest with reference and user session IDs
        
    Returns:
        CompareResponse with detailed comparison metrics
    """
    storage = get_storage()
    
    # Retrieve reference session
    ref_session = storage.get_session(request.session_id_reference)
    if ref_session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Reference session not found: {request.session_id_reference}"
        )
    
    # Retrieve user session
    user_session = storage.get_session(request.session_id_user)
    if user_session is None:
        raise HTTPException(
            status_code=404,
            detail=f"User session not found: {request.session_id_user}"
        )
    
    # Extract data from sessions
    ref_embedding = ref_session["embedding"]
    user_embedding = user_session["embedding"]
    
    ref_keypoints = ref_session["keypoints"]
    user_keypoints = user_session["keypoints"]
    
    ref_duration = ref_session["duration_seconds"]
    user_duration = user_session["duration_seconds"]
    
    # Calculate similarity score
    similarity_score = cosine_similarity(ref_embedding, user_embedding)
    
    # Calculate time difference
    time_difference = user_duration - ref_duration
    
    # Calculate movement deviations
    deviation_vector, deviation_stressed_joints = calculate_movement_deviation(
        ref_keypoints, user_keypoints
    )
    
    # Calculate ergonomic stressed joints for user
    ergonomic_stressed_joints = calculate_stressed_joints_ergonomic(user_keypoints)
    
    # Combine stressed joints (remove duplicates)
    all_stressed_joints = list(set(deviation_stressed_joints + ergonomic_stressed_joints))
    
    # Generate recommendations
    recommendations = generate_recommendations(
        similarity_score=similarity_score,
        time_difference=time_difference,
        stressed_joints=all_stressed_joints
    )
    
    # Return comparison results
    return CompareResponse(
        similarity_score=similarity_score,
        time_difference_seconds=time_difference,
        movement_deviation_vector=deviation_vector,
        stressed_joints=all_stressed_joints,
        recommended_improvements=recommendations
    )
