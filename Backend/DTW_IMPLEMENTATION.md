# DTW-Based Motion Comparison

## ✅ Successfully Integrated Dynamic Time Warping

### What is DTW?

**Dynamic Time Warping (DTW)** is an algorithm that finds the optimal alignment between two temporal sequences that may vary in speed. Perfect for comparing human movements that might be performed at different paces.

### Why DTW for Motion Analysis?

| Approach | Use Case | Limitations |
|----------|----------|-------------|
| **Cosine Similarity** | Static embeddings | ❌ Loses temporal information |
| **Frame-by-frame** | Same-length sequences | ❌ Fails if speeds differ |
| **DTW** | Variable-speed sequences | ✅ Handles timing variations |

## Architecture

### 1. Feature Extraction (`embedding.py`)

**Per-Frame Features (42 dimensions):**
- 8 joint angles (shoulders, elbows, hips, knees)
- 34 normalized positions (17 keypoints × 2 coords)

```python
def frame_feature_from_keypoints(keypoints_frame):
    # Normalize by torso center & length
    coords_norm = normalize_keypoints(kp)  # (17, 2)
    
    # Compute 8 key joint angles
    angles = compute_joint_angles(coords_norm)  # (8,)
    
    # Flatten positions
    pos_flat = coords_norm.flatten()  # (34,)
    
    # Combine: 8 + 34 = 42 dims
    return np.concatenate([angles, pos_flat])
```

**Sequence Processing:**
```python
# Convert video keypoints to feature matrix
frames = [{"keypoints": kp, "time_sec": t} for kp, t in ...]
X = sequence_to_feature_matrix(frames)  # (n_frames, 42)

# Apply temporal smoothing (3-frame moving average)
X_smooth = temporal_smoothing(X, window=3)
```

### 2. DTW Algorithm (`metrics.py`)

**Classic O(NM) Dynamic Programming:**
```python
def dtw_distance_matrix(D):
    n, m = D.shape
    cost = np.full((n+1, m+1), np.inf)
    cost[0,0] = 0.0
    
    # Fill cost matrix
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost[i,j] = D[i-1,j-1] + min(
                cost[i-1,j],    # insertion
                cost[i,j-1],    # deletion
                cost[i-1,j-1]   # match
            )
    
    # Backtrack to find optimal path
    path = backtrack(cost)
    return total_cost, path
```

**Similarity Mapping:**
```python
normalized_distance = total_cost / path_length
similarity = 1.0 / (1.0 + normalized_distance)  # 0-1 scale
```

### 3. Aligned Metrics

**Per-Joint Deviation:**
```python
for (i, j) in dtw_path:
    ref_frame = frames_ref[i]
    user_frame = frames_user[j]
    
    for joint in range(17):
        deviation = L2_distance(ref_frame[joint], user_frame[joint])
        joint_deviations[joint] += deviation
```

**Stressed Joint Detection:**
- Deviation > 0.25 (normalized units) → flagged as stressed
- Customizable per-joint thresholds

## API Changes

### Updated `/api/compare` Endpoint

**Before (Cosine Similarity):**
```json
{
  "similarity_score": 0.85,
  "time_difference_seconds": -2.3
}
```

**After (DTW-based):**
```json
{
  "similarity_score": 0.92,
  "time_difference_seconds": -2.3,
  "movement_deviation_vector": [0.1, 0.2, ...],
  "stressed_joints": ["left_shoulder", "left_elbow"],
  "recommended_improvements": [...]
}
```

### Backward Compatibility

✅ **All existing endpoints work unchanged**
- `POST /api/process-video` - Still returns embeddings
- `GET /api/session/{id}` - Still returns session data

The legacy `sequence_to_embedding()` function still works for backward compatibility.

## Performance

### Complexity

| Metric | Value |
|--------|-------|
| Feature extraction | O(N × 17) - linear in frames |
| DTW computation | O(N × M) - sequences length |
| Memory | O(N × M) for cost matrix |

### Optimization Tips

**For long sequences (>1000 frames):**

1. **Frame sampling:** Process every 2nd or 3rd frame
   ```python
   sampled_frames = frames[::2]  # Every 2nd frame
   ```

2. **Sakoe-Chiba band:** Constrain DTW search window
   ```python
   # Only consider alignments within ±10% time window
   window = int(0.1 * max(n, m))
   ```

3. **FastDTW approximation:** Trade accuracy for speed
   ```bash
   pip install fastdtw
   ```

## Tuning Parameters

### 1. Temporal Smoothing Window

```python
# Aggressive smoothing (more stable, less sensitive)
X_smooth = temporal_smoothing(X, window=5)

# Minimal smoothing (more responsive)
X_smooth = temporal_smoothing(X, window=2)
```

**Default:** `window=3` (good balance)

### 2. Stressed Joint Thresholds

```python
thresholds = {
    "left_shoulder": 0.2,   # More sensitive
    "left_elbow": 0.3,      # Less sensitive
    "left_knee": 0.25,      # Default
}

stressed = detect_stressed_joints(joint_devs, thresholds=thresholds)
```

### 3. Similarity Mapping

Current: `similarity = 1 / (1 + norm_cost)`

Alternative: `similarity = 100 * (1 - norm_cost / max_cost)`

## Testing DTW

### Test Script

```python
# Generate test data
frames_ref = [{"keypoints": [...], "time_sec": t} for t in range(10)]
frames_user = [{"keypoints": [...], "time_sec": t} for t in range(12)]

# Run DTW
from app.core.embedding import sequence_to_feature_matrix, temporal_smoothing
from app.core.metrics import run_dtw

X_ref = sequence_to_feature_matrix(frames_ref)
X_user = sequence_to_feature_matrix(frames_user)

X_ref = temporal_smoothing(X_ref, window=3)
X_user = temporal_smoothing(X_user, window=3)

result = run_dtw(X_ref, X_user)

print(f"Similarity: {result['similarity']:.2f}")
print(f"Path length: {len(result['path'])}")
```

## Migration Notes

### Files Modified

1. **`app/core/embedding.py`** - New DTW-optimized feature extraction
2. **`app/core/metrics.py`** - DTW implementation + aligned metrics
3. **`app/api/compare.py`** - Updated to use DTW pipeline
4. **`requirements.txt`** - Added `scipy>=1.11.0`

### Old Files Backed Up

- `app/core/embedding_old.py` - Original statistical aggregation
- `app/core/metrics_old.py` - Original interpolation-based metrics

### Rollback

```bash
# Restore old files if needed
mv app/core/embedding_old.py app/core/embedding.py
mv app/core/metrics_old.py app/core/metrics.py
```

## Advantages

✅ **Handles different speeds** - Worker can go faster/slower  
✅ **Better alignment** - Matches corresponding phases  
✅ **More accurate** - Frame-level correspondence  
✅ **Robust** - Works with variable-length sequences  

## Future Enhancements

- [ ] Sakoe-Chiba windowing for speed
- [ ] Multi-scale DTW for hierarchical analysis
- [ ] DTW + neural networks for learned distance metrics
- [ ] Real-time streaming DTW
- [ ] Confidence scores per alignment

## References

- Sakoe, H., & Chiba, S. (1978). Dynamic programming algorithm optimization for spoken word recognition.
- Müller, M. (2007). Information retrieval for music and motion.

---

**Your backend now uses state-of-the-art DTW for motion comparison! 🎯**
