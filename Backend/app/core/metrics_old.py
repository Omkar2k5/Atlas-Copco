"""
Metrics Calculation Module
Computes performance metrics, movement deviations, and stressed joints.
"""

import numpy as np
from typing import List, Tuple, Dict


def calculate_movement_deviation(
    reference_keypoints: List[List[List[float]]],
    user_keypoints: List[List[List[float]]]
) -> Tuple[List[float], List[str]]:
    """
    Calculate per-joint movement deviation between reference and user executions.
    
    Args:
        reference_keypoints: Reference keypoints [frame][joint][x, y, confidence]
        user_keypoints: User keypoints [frame][joint][x, y, confidence]
        
    Returns:
        Tuple of (deviation_vector, stressed_joints)
        deviation_vector: L2 distance per joint averaged across frames
        stressed_joints: List of joint names exceeding deviation threshold
    """
    # Normalize sequence lengths by interpolation
    ref_array = np.array(reference_keypoints)[:, :, :2]  # (frames, joints, 2)
    user_array = np.array(user_keypoints)[:, :, :2]
    
    ref_frames, num_joints = ref_array.shape[0], ref_array.shape[1]
    user_frames = user_array.shape[0]
    
    # Interpolate to match frame counts
    if ref_frames != user_frames:
        # Simple linear interpolation
        ref_indices = np.linspace(0, ref_frames - 1, user_frames)
        ref_array_interp = np.array([
            np.array([
                np.interp(ref_indices, np.arange(ref_frames), ref_array[:, j, coord])
                for coord in range(2)
            ]).T
            for j in range(num_joints)
        ]).transpose(1, 0, 2)
    else:
        ref_array_interp = ref_array
    
    # Calculate L2 distance per joint across all frames
    distances = np.linalg.norm(ref_array_interp - user_array, axis=2)  # (frames, joints)
    deviation_per_joint = np.mean(distances, axis=0)  # (joints,)
    
    # Identify stressed joints (deviation > threshold)
    threshold = np.percentile(deviation_per_joint, 75)  # Top 25% deviations
    stressed_indices = np.where(deviation_per_joint > threshold)[0]
    
    joint_names = get_joint_names()
    stressed_joints = [joint_names[i] for i in stressed_indices if i < len(joint_names)]
    
    return deviation_per_joint.tolist(), stressed_joints


def calculate_stressed_joints_ergonomic(
    keypoints: List[List[List[float]]]
) -> List[str]:
    """
    Identify joints under stress based on ergonomic angle thresholds.
    
    Args:
        keypoints: Keypoints sequence [frame][joint][x, y, confidence]
        
    Returns:
        List of joint names that exceed ergonomic thresholds
    """
    stressed = set()
    
    for frame_kpts in keypoints:
        kpts = np.array(frame_kpts)[:, :2]
        
        # Check neck angle (head forward posture)
        # MoveNet: nose (0), left shoulder (5), right shoulder (6)
        if len(kpts) < 13:
            continue  # Skip frames with insufficient keypoints
        
        nose = kpts[0]
        left_shoulder = kpts[5]
        right_shoulder = kpts[6]
        shoulder_center = (left_shoulder + right_shoulder) / 2
        
        # Neck angle from vertical
        neck_vector = nose - shoulder_center
        vertical = np.array([0, -1])
        cos_angle = np.dot(neck_vector, vertical) / (np.linalg.norm(neck_vector) * np.linalg.norm(vertical) + 1e-8)
        neck_angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        # Threshold: > 30 degrees from vertical
        if neck_angle > np.radians(30):
            stressed.add("neck")
        
        # Check shoulder elevation
        # Compare shoulder height with hip height
        # MoveNet: left hip (11), right hip (12)
        left_hip = kpts[11]
        right_hip = kpts[12]
        
        shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_y = (left_hip[1] + right_hip[1]) / 2
        
        # If shoulders are elevated (y is smaller in image coordinates)
        torso_length = abs(shoulder_y - hip_y)
        if torso_length > 0:
            # Check if shoulders are raised > 10% of torso length above normal
            normal_shoulder_y = hip_y - torso_length
            if shoulder_y < normal_shoulder_y - 0.1 * torso_length:
                stressed.add("left_shoulder")
                stressed.add("right_shoulder")
        
        # Check elbow angles for awkward positions
        # MoveNet: left shoulder (5), left elbow (7), left wrist (9)
        left_shoulder_pos = kpts[5]
        left_elbow_pos = kpts[7]
        left_wrist_pos = kpts[9]
        
        v1 = left_shoulder_pos - left_elbow_pos
        v2 = left_wrist_pos - left_elbow_pos
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        left_elbow_angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        # Extreme flexion (< 45 degrees) or full extension (> 170 degrees)
        if left_elbow_angle < np.radians(45) or left_elbow_angle > np.radians(170):
            stressed.add("left_elbow")
        
        # Right elbow
        # MoveNet: right shoulder (6), right elbow (8), right wrist (10)
        right_shoulder_pos = kpts[6]
        right_elbow_pos = kpts[8]
        right_wrist_pos = kpts[10]
        
        v1 = right_shoulder_pos - right_elbow_pos
        v2 = right_wrist_pos - right_elbow_pos
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        right_elbow_angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        if right_elbow_angle < np.radians(45) or right_elbow_angle > np.radians(170):
            stressed.add("right_elbow")
        
        # Check spine alignment (simplified)
        # Compare shoulder center to hip center - should be relatively aligned
        spine_vector = shoulder_center - (left_hip + right_hip) / 2
        spine_angle = np.arctan2(abs(spine_vector[0]), abs(spine_vector[1]))
        
        # Threshold: > 15 degrees from vertical
        if spine_angle > np.radians(15):
            stressed.add("spine")
    
    return list(stressed)


def generate_recommendations(
    similarity_score: float,
    time_difference: float,
    stressed_joints: List[str]
) -> List[str]:
    """
    Generate improvement recommendations based on analysis.
    
    Args:
        similarity_score: Overall movement similarity (0-1)
        time_difference: Time difference from reference in seconds
        stressed_joints: List of joints under stress
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Similarity-based recommendations
    if similarity_score < 0.6:
        recommendations.append("Review the reference video and focus on matching the overall movement pattern")
    elif similarity_score < 0.8:
        recommendations.append("Good progress! Refine your movements to more closely match the reference")
    
    # Time-based recommendations
    if abs(time_difference) > 5:
        if time_difference > 0:
            recommendations.append(f"Try to speed up - you're {abs(time_difference):.1f}s slower than the reference")
        else:
            recommendations.append(f"Slow down to match the reference pace - you're {abs(time_difference):.1f}s faster")
    
    # Joint-specific recommendations
    joint_recommendations = {
        "neck": "Keep your head aligned with your spine to reduce neck strain",
        "left_shoulder": "Relax your left shoulder - avoid unnecessary elevation",
        "right_shoulder": "Relax your right shoulder - avoid unnecessary elevation",
        "left_elbow": "Check your left elbow angle - avoid extreme positions",
        "right_elbow": "Check your right elbow angle - avoid extreme positions",
        "spine": "Maintain better spinal alignment - keep your torso upright",
        "left_knee": "Be mindful of your left knee position during the movement",
        "right_knee": "Be mindful of your right knee position during the movement"
    }
    
    for joint in stressed_joints:
        if joint in joint_recommendations:
            recommendations.append(joint_recommendations[joint])
    
    if not recommendations:
        recommendations.append("Excellent execution! Your movement closely matches the reference")
    
    return recommendations


def get_joint_names() -> List[str]:
    """Return list of joint names in MoveNet order (17 keypoints)."""
    return [
        "nose",           # 0
        "left_eye",       # 1
        "right_eye",      # 2
        "left_ear",       # 3
        "right_ear",      # 4
        "left_shoulder",  # 5
        "right_shoulder", # 6
        "left_elbow",     # 7
        "right_elbow",    # 8
        "left_wrist",     # 9
        "right_wrist",    # 10
        "left_hip",       # 11
        "right_hip",      # 12
        "left_knee",      # 13
        "right_knee",     # 14
        "left_ankle",     # 15
        "right_ankle"     # 16
    ]
