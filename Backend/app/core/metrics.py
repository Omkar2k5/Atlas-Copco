"""
Metrics Calculation Module with DTW Implementation
Computes performance metrics, movement deviations, and stressed joints.
"""

from typing import Tuple, List, Dict
import numpy as np

def pairwise_distances(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute pairwise Euclidean distances between frames of A (n, d) and B (m, d)."""
    try:
        from scipy.spatial.distance import cdist
        return cdist(A, B, metric='euclidean')
    except Exception:
        # fallback
        d = np.sum((A[:, None, :] - B[None, :, :])**2, axis=2)
        return np.sqrt(d)

def dtw_distance_matrix(D: np.ndarray, window: int = None) -> Tuple[float, List[Tuple[int,int]], np.ndarray]:
    """
    Dynamic time warping with optional Sakoe-Chiba band constraint.
    
    Args:
        D: Distance matrix (n x m)
        window: Sakoe-Chiba window width (None = no constraint)
                Recommended: 10-20% of max(n,m) for long sequences
    
    Returns:
        (total_cost, path, cost_matrix)
    """
    n, m = D.shape
    cost = np.full((n+1, m+1), np.inf, dtype=float)
    cost[0,0] = 0.0
    
    # Determine window constraint
    if window is None:
        window = max(n, m)  # No constraint
    
    # Fill with Sakoe-Chiba band
    for i in range(1, n+1):
        # Compute valid j range for this i
        j_start = max(1, i - window)
        j_end = min(m + 1, i + window + 1)
        
        for j in range(j_start, j_end):
            choices = (cost[i-1,j], cost[i,j-1], cost[i-1,j-1])
            cost[i,j] = D[i-1, j-1] + min(choices)
    
    total_cost = cost[n, m]
    
    # Backtrack
    i, j = n, m
    path = []
    while i > 0 and j > 0:
        path.append((i-1, j-1))
        # determine step
        neighbors = [(cost[i-1,j-1], i-1,j-1), (cost[i-1,j], i-1,j), (cost[i,j-1], i,j-1)]
        prev_cost, pi, pj = min(neighbors, key=lambda x: x[0])
        i, j = pi, pj
    path.reverse()
    return float(total_cost), path, cost[1:,1:]

def run_dtw(A: np.ndarray, B: np.ndarray, window: int = None, use_fastdtw: bool = False) -> Dict:
    """
    Runs DTW between sequences A (n,d) and B (m,d).
    
    Args:
        A: Reference sequence (n, d)
        B: User sequence (m, d)
        window: Sakoe-Chiba window width (None = auto-calculate for long sequences)
                Recommended: 10-20% of max(n,m)
        use_fastdtw: Try to use FastDTW approximation if available (faster for long sequences)
    
    Returns:
        Dict with distance, similarity, path, and cost_matrix
    """
    if A.size == 0 or B.size == 0:
        return {"distance": float("inf"), "similarity": 0.0, "path": [], "mapping": []}
    
    n, m = A.shape[0], B.shape[0]
    
    # Auto-calculate window for long sequences
    if window is None and max(n, m) > 500:
        window = int(0.15 * max(n, m))  # 15% window for long sequences
    
    # Try FastDTW for very long sequences
    if use_fastdtw and max(n, m) > 1000:
        try:
            from fastdtw import fastdtw
            distance, path = fastdtw(A, B, dist=lambda x, y: np.linalg.norm(x - y))
            path_len = len(path) if len(path) > 0 else 1
            norm_cost = distance / path_len
            similarity = 1.0 / (1.0 + norm_cost)
            return {
                "distance": float(distance),
                "normalized_distance": float(norm_cost),
                "similarity": float(similarity),
                "path": path,
                "cost_matrix": None,  # FastDTW doesn't return cost matrix
                "method": "fastdtw"
            }
        except ImportError:
            pass  # Fall back to standard DTW
    
    # Standard DTW with optional window
    D = pairwise_distances(A, B)  # (n,m)
    total_cost, path, cost_matrix = dtw_distance_matrix(D, window=window)
    path_len = len(path) if len(path) > 0 else 1
    norm_cost = total_cost / path_len
    
    # similarity mapping: convert to 0..1 where higher=more similar
    similarity = 1.0 / (1.0 + norm_cost)
    
    return {
        "distance": float(total_cost),
        "normalized_distance": float(norm_cost),
        "similarity": float(similarity),
        "similarity_percentage": float(100 * similarity),  # 0-100 scale
        "path": path,
        "cost_matrix": cost_matrix,
        "method": "dtw" if window is None else f"dtw_window_{window}"
    }

def compute_time_deviation(frames_meta_A: List[Dict], frames_meta_B: List[Dict], path: List[Tuple[int,int]]) -> Dict:
    """
    Using frame timestamps (time_sec) map aligned frames and compute:
    - average_time_ratio = mean(time_B / time_A) across aligned pairs (helps find speed difference)
    - total_time_A, total_time_B, ratio
    """
    times_A = [f.get("time_sec", i) for i,f in enumerate(frames_meta_A)]
    times_B = [f.get("time_sec", i) for i,f in enumerate(frames_meta_B)]
    ratios = []
    for i,j in path:
        ta = times_A[i]
        tb = times_B[j]
        if ta <= 1e-6:
            continue
        ratios.append(tb / ta)
    if len(ratios) == 0:
        avg_ratio = 1.0
    else:
        avg_ratio = float(np.mean(ratios))
    total_A = times_A[-1] if times_A else 0.0
    total_B = times_B[-1] if times_B else 0.0
    return {"avg_time_ratio": avg_ratio, "total_time_A": total_A, "total_time_B": total_B}

def per_joint_deviation(frames_A: List[Dict], frames_B: List[Dict], path: List[Tuple[int,int]]) -> Dict:
    """
    Compute per-joint average L2 deviation across aligned frames.
    Returns dict {joint_name: avg_deviation}
    """
    KP_NAMES = [
        "nose","left_eye","right_eye","left_ear","right_ear",
        "left_shoulder","right_shoulder","left_elbow","right_elbow",
        "left_wrist","right_wrist","left_hip","right_hip",
        "left_knee","right_knee","left_ankle","right_ankle"
    ]
    n_joints = len(KP_NAMES)
    deviations = np.zeros(n_joints, dtype=float)
    counts = np.zeros(n_joints, dtype=int)
    for i,j in path:
        ka = np.array(frames_A[i]["keypoints"])[:,:2]
        kb = np.array(frames_B[j]["keypoints"])[:,:2]
        # both are normalized? assume pre-normalized by embedding pipeline
        for idx in range(n_joints):
            if idx >= ka.shape[0] or idx >= kb.shape[0]:
                continue
            da = ka[idx]
            db = kb[idx]
            d = np.linalg.norm(da - db)
            deviations[idx] += d
            counts[idx] += 1
    avg_dev = {}
    for idx, name in enumerate(KP_NAMES):
        avg = float(deviations[idx] / counts[idx]) if counts[idx] > 0 else 0.0
        avg_dev[name] = avg
    return avg_dev

def detect_stressed_joints(avg_joint_devs: Dict[str,float], angle_changes_summary: Dict[str,float]=None, thresholds: Dict[str,float]=None) -> List[str]:
    """
    Simple heuristic: joints with avg deviation above threshold flagged as stressed.
    thresholds: mapping joint -> threshold (default 0.25)
    """
    if thresholds is None:
        thresholds = {k:0.25 for k in avg_joint_devs.keys()}  # default threshold
    stressed = []
    for joint, val in avg_joint_devs.items():
        th = thresholds.get(joint, 0.25)
        if val > th:
            stressed.append(joint)
    # Optionally include angle-based heuristics (e.g., repeated extreme knee flexion)
    return stressed


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
