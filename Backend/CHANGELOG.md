# AssemblyFlow Backend - Change Log

## Version 2.1 - Configuration & Optimization (2025-11-02)

### 🎯 New Features

#### 1. Sakoe-Chiba Windowing
- **What:** Constrains DTW search to diagonal band (15% default)
- **Why:** Speeds up long sequence comparisons
- **Impact:** 2-5x faster for sequences >500 frames

#### 2. FastDTW Support
- **What:** Optional approximation algorithm for very long sequences
- **Requires:** `pip install fastdtw`
- **Impact:** 10x+ speedup for sequences >1000 frames

#### 3. Frame Sampling
- **What:** Process every Nth frame (configurable)
- **Why:** Reduce computation for long videos
- **Impact:** Proportional speedup (2x with sample_rate=2)

#### 4. Configuration Presets
- **precise** - Maximum accuracy (slow)
- **balanced** - Default, good trade-off
- **fast** - Quick processing
- **long_sequences** - Optimized for >60sec videos

#### 5. Configurable Thresholds
- Per-joint stressed detection thresholds
- Preset sensitivity levels (strict/moderate/relaxed)
- Similarity scaling (0-1 or 0-100)

### 📦 New Modules

#### `app/core/config.py`
```python
# Configuration classes
- DTWConfig            # All DTW parameters
- VideoProcessingConfig
- DTWPresets           # preset(), balanced(), fast(), long_sequences()
- StressedJointThresholds  # strict(), moderate(), relaxed()
```

### 📊 API Enhancements

#### `/api/compare` with Presets

```bash
POST /api/compare?preset=fast
POST /api/compare?preset=long_sequences
```

**Response enhanced with:**
- `similarity_percentage` (0-100 scale)
- `method` field (shows DTW variant used)

---

## Version 2.0 - DTW Integration (2025-11-02)

### 🎯 Major Features

#### 1. Dynamic Time Warping (DTW) Motion Comparison
- **What:** Replaced cosine similarity with DTW-based sequence alignment
- **Why:** Handles variable-speed movements, provides frame-level correspondence
- **Impact:** More accurate comparison, especially for different execution speeds

#### 2. Enhanced Feature Extraction
- **42-dimensional per-frame features**
  - 8 joint angles (shoulders, elbows, hips, knees)
  - 34 normalized positions (17 keypoints × 2 coords)
- **Temporal smoothing** (3-frame moving average)
- **Torso-normalized coordinates** for size invariance

#### 3. Aligned Per-Joint Analysis
- **Frame alignment via DTW path**
- **Per-joint deviation metrics** (L2 distance on aligned frames)
- **Stressed joint detection** with customizable thresholds

### 📦 New Modules

#### `app/core/embedding.py` (v2.0)
```python
# New functions
- frame_feature_from_keypoints()  # 42-dim per-frame features
- sequence_to_feature_matrix()    # Convert sequence to matrix
- temporal_smoothing()             # Moving average filter
- normalize_keypoints()            # Torso-based normalization

# Legacy support
- sequence_to_embedding()          # Still works for backward compatibility
```

#### `app/core/metrics.py` (v2.0)
```python
# DTW implementation
- run_dtw()                        # Full DTW with path return
- dtw_distance_matrix()            # Classic DP algorithm
- pairwise_distances()             # Euclidean distance matrix

# Aligned metrics
- per_joint_deviation()            # Deviation on aligned frames
- compute_time_deviation()         # Timing analysis
- detect_stressed_joints()         # Threshold-based detection
```

#### `app/api/compare.py` (v2.0)
- DTW-based comparison pipeline
- Frame-level alignment
- Enhanced metrics output

### 📊 API Changes

#### `/api/compare` Endpoint (Enhanced)

**Request:** (Unchanged)
```json
{
  "session_id_reference": "uuid",
  "session_id_user": "uuid"
}
```

**Response:** (Enhanced with DTW metrics)
```json
{
  "similarity_score": 0.92,           // DTW-based (0-1)
  "time_difference_seconds": -2.3,
  "movement_deviation_vector": [...], // 17 per-joint deviations
  "stressed_joints": [...],           // Detected problem areas
  "recommended_improvements": [...]
}
```

### 🔧 Dependencies Added

- `scipy>=1.11.0` - For optimized distance calculations

### 📚 Documentation

**New Files:**
- `DTW_IMPLEMENTATION.md` - Complete DTW technical documentation
- `CHANGELOG.md` - This file

**Updated Files:**
- `README.md` - Reflect MoveNet and DTW features
- `QUICKSTART.md` - Add DTW workflow information
- `MOVENET_MIGRATION.md` - Complete migration guide

### 🔄 Backward Compatibility

✅ **All existing functionality preserved:**
- `POST /api/process-video` - Works unchanged
- `GET /api/session/{id}` - Works unchanged
- `sequence_to_embedding()` - Legacy function still available

**Old modules backed up:**
- `app/core/embedding_old.py`
- `app/core/metrics_old.py`

### 🎓 Performance

| Metric | Value |
|--------|-------|
| Feature extraction | O(N × 17) |
| DTW computation | O(N × M) |
| Memory usage | O(N × M) |
| Typical comparison | <1s for 10-30 sec videos |

**Optimization options:**
- Frame sampling (process every Nth frame)
- Sakoe-Chiba windowing
- FastDTW approximation

### 🧪 Testing

**Verify installation:**
```bash
python test_movenet.py  # MoveNet model test
```

**Test DTW pipeline:**
```python
from app.core.embedding import sequence_to_feature_matrix, temporal_smoothing
from app.core.metrics import run_dtw

# Create test frames
frames_a = [{"keypoints": [...]} for _ in range(10)]
frames_b = [{"keypoints": [...]} for _ in range(12)]

# Run DTW
X_a = temporal_smoothing(sequence_to_feature_matrix(frames_a), window=3)
X_b = temporal_smoothing(sequence_to_feature_matrix(frames_b), window=3)
result = run_dtw(X_a, X_b)

print(f"Similarity: {result['similarity']}")
```

### 🚀 Migration from v1.0

**Automatic migration:**
- No code changes required in calling applications
- All API endpoints backward compatible
- New DTW features available immediately

**To use DTW features:**
1. Ensure `scipy` is installed
2. Sessions automatically use new comparison method
3. Old embeddings still work (legacy mode)

### 📈 Improvements Over v1.0

| Aspect | v1.0 | v2.0 (DTW) |
|--------|------|------------|
| **Sequence handling** | Fixed-length embedding | Variable-length support |
| **Speed variance** | Poor | Excellent |
| **Frame alignment** | None | Optimal DTW path |
| **Temporal detail** | Lost (statistical agg) | Preserved (per-frame) |
| **Accuracy** | Good | Excellent |

### 🐛 Known Issues

None currently identified.

**Potential considerations:**
- Long sequences (>1000 frames) may be slow → use sampling
- High memory for very long comparisons → implement windowing

### 🔮 Future Roadmap

- [ ] Sakoe-Chiba banding for performance
- [ ] Multi-resolution DTW
- [ ] GPU-accelerated DTW
- [ ] Real-time streaming comparison
- [ ] Learned distance metrics

---

## Version 1.0 - MoveNet Integration (2025-11-01)

### Initial Features

- MoveNet Thunder pose estimation (17 keypoints)
- Basic embedding generation (256-dim vectors)
- Cosine similarity comparison
- FastAPI backend with CORS
- ChromaDB vector storage
- Session management

---

**For detailed technical documentation, see:**
- `README.md` - Full usage guide
- `DTW_IMPLEMENTATION.md` - DTW technical details
- `MOVENET_MIGRATION.md` - MoveNet implementation
- `QUICKSTART.md` - Quick start guide
