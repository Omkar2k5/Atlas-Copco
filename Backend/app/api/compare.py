"""
Compare API Endpoint
Compares two pose execution sessions using DTW-based analysis.
"""

from fastapi import APIRouter, HTTPException, Query
import numpy as np
from typing import Optional

from app.schemas.compare import CompareRequest, CompareResponse
from app.db.storage import get_storage
from app.core.embedding import sequence_to_feature_matrix, temporal_smoothing
from app.core.metrics import (
    run_dtw,
    compute_time_deviation,
    per_joint_deviation,
    detect_stressed_joints,
    generate_recommendations
)
from app.core.config import get_dtw_config, DTWPresets


router = APIRouter()


@router.post("/compare", response_model=CompareResponse)
async def compare_sessions(
    request: CompareRequest,
    preset: Optional[str] = Query(None, description="DTW preset: 'precise', 'balanced', 'fast', or 'long_sequences'")
):
    """
    Compare two pose execution sessions using DTW-based analysis.
    
    Analyzes:
    - Movement similarity (DTW-based alignment)
    - Time difference and pacing
    - Per-joint movement deviations (aligned frames)
    - Stressed/strained joints
    - Actionable improvement recommendations
    
    Args:
        request: CompareRequest with reference and user session IDs
        
    Returns:
        CompareResponse with detailed comparison metrics
    """
    # Load configuration
    if preset:
        preset_map = {
            "precise": DTWPresets.precise(),
            "balanced": DTWPresets.balanced(),
            "fast": DTWPresets.fast(),
            "long_sequences": DTWPresets.long_sequences()
        }
        config = preset_map.get(preset, get_dtw_config())
    else:
        config = get_dtw_config()
    
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
    
    # Extract keypoints and prepare frame structures
    ref_keypoints = ref_session["keypoints"]
    user_keypoints = user_session["keypoints"]
    ref_duration = ref_session["duration_seconds"]
    user_duration = user_session["duration_seconds"]
    
    # Convert keypoints to frame format for DTW
    frames_ref = [
        {"keypoints": kp, "time_sec": (i / len(ref_keypoints)) * ref_duration}
        for i, kp in enumerate(ref_keypoints)
    ]
    frames_user = [
        {"keypoints": kp, "time_sec": (i / len(user_keypoints)) * user_duration}
        for i, kp in enumerate(user_keypoints)
    ]
    
    # Convert to feature matrices (with sampling)
    X_ref = sequence_to_feature_matrix(frames_ref, sample_rate=config.frame_sample_rate)
    X_user = sequence_to_feature_matrix(frames_user, sample_rate=config.frame_sample_rate)
    
    # Apply temporal smoothing
    X_ref_smooth = temporal_smoothing(X_ref, window=config.smoothing_window)
    X_user_smooth = temporal_smoothing(X_user, window=config.smoothing_window)
    
    # Run DTW alignment with config
    window_size = config.get_window_size(max(X_ref_smooth.shape[0], X_user_smooth.shape[0]))
    dtw_result = run_dtw(
        X_ref_smooth, 
        X_user_smooth, 
        window=window_size,
        use_fastdtw=config.use_fastdtw
    )
    similarity_score = dtw_result["similarity"]
    
    # Compute time deviation analysis
    time_analysis = compute_time_deviation(frames_ref, frames_user, dtw_result["path"])
    time_difference = user_duration - ref_duration
    
    # Compute per-joint deviations using aligned frames
    joint_deviations = per_joint_deviation(frames_ref, frames_user, dtw_result["path"])
    
    # Detect stressed joints with config thresholds
    thresholds = {k: config.get_joint_threshold(k) for k in joint_deviations.keys()}
    stressed_joints = detect_stressed_joints(joint_deviations, thresholds=thresholds)
    
    # Convert joint deviations dict to list for response
    deviation_vector = [joint_deviations.get(f"joint_{i}", 0.0) for i in range(17)]
    
    # Generate recommendations
    recommendations = generate_recommendations(
        similarity_score=similarity_score,
        time_difference=time_difference,
        stressed_joints=stressed_joints
    )
    
    # Return comparison results
    return CompareResponse(
        similarity_score=similarity_score,
        time_difference_seconds=time_difference,
        movement_deviation_vector=deviation_vector,
        stressed_joints=stressed_joints,
        recommended_improvements=recommendations
    )
