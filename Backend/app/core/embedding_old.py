"""
Embedding Generation Module
Converts per-frame MoveNet keypoints into frame-level features.
Supports DTW-based sequence comparison.
"""

from typing import List, Dict, Tuple
import numpy as np
import math

# Indices for MoveNet 17 keypoints
KP = {
    "nose": 0, "left_eye":1, "right_eye":2, "left_ear":3, "right_ear":4,
    "left_shoulder":5, "right_shoulder":6, "left_elbow":7, "right_elbow":8,
    "left_wrist":9, "right_wrist":10, "left_hip":11, "right_hip":12,
    "left_knee":13, "right_knee":14, "left_ankle":15, "right_ankle":16
}

def to_np(keypoints_frame: List[Tuple[float,float,float]]) -> np.ndarray:
    """Return (17,3) numpy array from list-of-tuples."""
    return np.array(keypoints_frame, dtype=float)  # shape (17,3)

def torso_center_and_scale(kp: np.ndarray) -> Tuple[np.ndarray,float]:
    """Compute torso midpoint and torso length (distance between mid-shoulder and mid-hip)."""
    ls = kp[KP["left_shoulder"], :2]
    rs = kp[KP["right_shoulder"], :2]
    lh = kp[KP["left_hip"], :2]
    rh = kp[KP["right_hip"], :2]
    mid_sh = (ls + rs) / 2.0
    mid_hip = (lh + rh) / 2.0
    center = (mid_sh + mid_hip) / 2.0
    torso_len = np.linalg.norm(mid_sh - mid_hip)
    if torso_len < 1e-6:
        torso_len = 1.0
    return center, float(torso_len)

def normalize_keypoints(kp: np.ndarray) -> np.ndarray:
    """Translate/scale keypoints -> center at torso midpoint, scale by torso_len. Returns (17,2)."""
    center, scale = torso_center_and_scale(kp)
    coords = kp[:, :2] - center  # translate
    coords = coords / scale      # scale
    return coords  # (17,2)

def angle_between(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Return angle at b formed by points a-b-c in radians (0..pi)."""
    ba = a - b
    bc = c - b
    # handle degenerate
    na = np.linalg.norm(ba)
    nb = np.linalg.norm(bc)
    if na < 1e-6 or nb < 1e-6:
        return 0.0
    cosang = np.dot(ba, bc) / (na * nb)
    cosang = np.clip(cosang, -1.0, 1.0)
    return float(np.arccos(cosang))

def compute_joint_angles(kp_norm: np.ndarray) -> np.ndarray:
    """Compute a vector of selected joint angles (radians) from normalized (17,2) coords."""
    # Example angles: left_shoulder (elbow-shoulder-hip), right_shoulder, left_elbow (shoulder-elbow-wrist), right_elbow,
    # left_hip (shoulder-hip-knee), right_hip, left_knee (hip-knee-ankle), right_knee.
    a = []
    # left_shoulder angle: left_elbow - left_shoulder - left_hip
    a.append(angle_between(kp_norm[KP["left_elbow"]], kp_norm[KP["left_shoulder"]], kp_norm[KP["left_hip"]]))
    a.append(angle_between(kp_norm[KP["right_elbow"]], kp_norm[KP["right_shoulder"]], kp_norm[KP["right_hip"]]))
    # left_elbow and right_elbow
    a.append(angle_between(kp_norm[KP["left_shoulder"]], kp_norm[KP["left_elbow"]], kp_norm[KP["left_wrist"]]))
    a.append(angle_between(kp_norm[KP["right_shoulder"]], kp_norm[KP["right_elbow"]], kp_norm[KP["right_wrist"]]))
    # hips
    a.append(angle_between(kp_norm[KP["left_shoulder"]], kp_norm[KP["left_hip"]], kp_norm[KP["left_knee"]]))
    a.append(angle_between(kp_norm[KP["right_shoulder"]], kp_norm[KP["right_hip"]], kp_norm[KP["right_knee"]]))
    # knees
    a.append(angle_between(kp_norm[KP["left_hip"]], kp_norm[KP["left_knee"]], kp_norm[KP["left_ankle"]]))
    a.append(angle_between(kp_norm[KP["right_hip"]], kp_norm[KP["right_knee"]], kp_norm[KP["right_ankle"]]))
    return np.array(a, dtype=float)  # shape (8,)

def frame_feature_from_keypoints(keypoints_frame: List[Tuple[float,float,float]]) -> np.ndarray:
    """Produce a single feature vector for a frame."""
    kp = to_np(keypoints_frame)  # (17,3)
    coords_norm = normalize_keypoints(kp)  # (17,2)
    angles = compute_joint_angles(coords_norm)  # (8,)
    # Flatten normalized coords (x,y) for selected joints (optionally all joints)
    # Use only joint positions without confidence to keep features stable; scale later if needed
    pos_flat = coords_norm.flatten()  # 34 dims
    # Combine angles + pos -> final vector
    feat = np.concatenate([angles, pos_flat])  # 8 + 34 = 42 dims
    return feat

def sequence_to_feature_matrix(frames: List[Dict]) -> np.ndarray:
    """Convert list of frames (each with 'keypoints' list) to (n_frames, feature_dim) matrix."""
    feats = []
    for f in frames:
        kp = f.get("keypoints", [])
        feat = frame_feature_from_keypoints(kp)
        feats.append(feat)
    return np.vstack(feats) if feats else np.zeros((0, 42), dtype=float)

def temporal_smoothing(feat_matrix: np.ndarray, window: int = 3) -> np.ndarray:
    """Apply simple moving average smoothing over frames (axis=0)."""
    if feat_matrix.shape[0] < 2 or window <= 1:
        return feat_matrix
    kernel = np.ones(window) / window
    out = np.copy(feat_matrix)
    for i in range(feat_matrix.shape[1]):
        col = feat_matrix[:, i]
        sm = np.convolve(col, kernel, mode='same')
        out[:, i] = sm
    return out


# Legacy function for backward compatibility with existing API
def calculate_joint_angles_legacy(keypoints: List[List[List[float]]]) -> np.ndarray:
    """
    Calculate joint angles for each frame.
    
    Args:
        keypoints: List[frame][joint][x, y, confidence]
        
    Returns:
        Array of shape (num_frames, num_angles) containing joint angles
    """
    angles_per_frame = []
    
    for frame_kpts in keypoints:
        frame_angles = []
        
        # Convert to numpy for easier computation
        kpts = np.array(frame_kpts)[:, :2]  # Take only x, y
        
        # Define joint triplets for angle calculation (parent, joint, child)
        # MoveNet indices (17 keypoints)
        angle_triplets = [
            # Arms
            (5, 7, 9),    # left shoulder, elbow, wrist
            (6, 8, 10),   # right shoulder, elbow, wrist
            # Legs
            (11, 13, 15), # left hip, knee, ankle
            (12, 14, 16), # right hip, knee, ankle
            # Torso
            (5, 11, 13),  # left shoulder, hip, knee
            (6, 12, 14),  # right shoulder, hip, knee
            # Neck/Shoulder
            (0, 5, 7),    # nose, left shoulder, left elbow
            (0, 6, 8),    # nose, right shoulder, right elbow
        ]
        
        for p1_idx, p2_idx, p3_idx in angle_triplets:
            p1, p2, p3 = kpts[p1_idx], kpts[p2_idx], kpts[p3_idx]
            
            # Calculate vectors
            v1 = p1 - p2
            v2 = p3 - p2
            
            # Calculate angle using dot product
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            frame_angles.append(angle)
        
        angles_per_frame.append(frame_angles)
    
    return np.array(angles_per_frame)


def calculate_velocity_features(keypoints: List[List[List[float]]]) -> np.ndarray:
    """
    Calculate velocity features (frame-to-frame movement).
    
    Args:
        keypoints: List[frame][joint][x, y, confidence]
        
    Returns:
        Velocity features array
    """
    kpts_array = np.array(keypoints)[:, :, :2]  # (frames, joints, 2)
    
    # Calculate frame-to-frame differences
    velocities = np.diff(kpts_array, axis=0)
    
    # Calculate velocity magnitude per joint
    velocity_magnitudes = np.linalg.norm(velocities, axis=2)  # (frames-1, joints)
    
    return velocity_magnitudes


def sequence_to_embedding(keypoints: List[List[List[float]]]) -> List[float]:
    """
    Convert variable-length keypoint sequence to fixed-length embedding vector.
    
    Strategy:
    1. Calculate joint angles for each frame
    2. Calculate velocity features
    3. Compute statistical features (mean, std, min, max) across time
    4. Flatten into single embedding vector
    
    Args:
        keypoints: List[frame][joint][x, y, confidence]
        
    Returns:
        Fixed-length embedding vector as list
    """
    if not keypoints or len(keypoints) == 0:
        # Return zero embedding if no keypoints
        return [0.0] * 256
    
    # Calculate joint angles
    angles = calculate_joint_angles(keypoints)  # (num_frames, num_angles)
    
    # Calculate velocity features
    velocities = calculate_velocity_features(keypoints)  # (num_frames-1, num_joints)
    
    # Statistical aggregation
    features = []
    
    # Angle statistics
    if angles.shape[0] > 0:
        features.extend(np.mean(angles, axis=0).tolist())
        features.extend(np.std(angles, axis=0).tolist())
        features.extend(np.min(angles, axis=0).tolist())
        features.extend(np.max(angles, axis=0).tolist())
    
    # Velocity statistics
    if velocities.shape[0] > 0:
        features.extend(np.mean(velocities, axis=0).tolist())
        features.extend(np.std(velocities, axis=0).tolist())
    
    # Positional statistics (using raw keypoints)
    kpts_array = np.array(keypoints)[:, :, :2]  # (frames, joints, 2)
    features.extend(np.mean(kpts_array, axis=0).flatten().tolist())
    features.extend(np.std(kpts_array, axis=0).flatten().tolist())
    
    # Pad or truncate to fixed size (256 dimensions)
    target_size = 256
    if len(features) < target_size:
        features.extend([0.0] * (target_size - len(features)))
    else:
        features = features[:target_size]
    
    return features


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Similarity score between 0 and 1
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    
    # Convert from [-1, 1] to [0, 1]
    return (similarity + 1.0) / 2.0
