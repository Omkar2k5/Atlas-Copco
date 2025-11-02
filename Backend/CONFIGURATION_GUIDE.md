# Configuration & Tuning Guide

## Overview

AssemblyFlow backend provides extensive configuration options to optimize DTW comparison for different scenarios: precise analysis, fast processing, or long sequences.

## Quick Start

### Using Presets

The easiest way to configure DTW is using presets via API query parameters:

```bash
# Balanced (default)
curl -X POST "http://localhost:8000/api/compare?preset=balanced" \
  -H "Content-Type: application/json" \
  -d '{"session_id_reference": "ref-id", "session_id_user": "user-id"}'

# High precision (slower)
curl -X POST "http://localhost:8000/api/compare?preset=precise" ...

# Fast processing
curl -X POST "http://localhost:8000/api/compare?preset=fast" ...

# Long videos (>60 sec)
curl -X POST "http://localhost:8000/api/compare?preset=long_sequences" ...
```

## Configuration Parameters

### 1. Frame Sampling (`frame_sample_rate`)

**What:** Process every Nth frame instead of all frames.

**Values:**
- `1` - All frames (most accurate, slowest)
- `2` - Every 2nd frame (good balance)
- `3-5` - Every 3rd-5th frame (fast, for long videos)

**When to use:**
- `1` - Precise, slow motions (assembly steps)
- `2` - Normal speed motions
- `3-5` - Fast motions or videos >60 seconds

**Example:**
```python
from app.core.config import DTWConfig
config = DTWConfig(frame_sample_rate=2)  # Process every 2nd frame
```

---

### 2. Temporal Smoothing (`smoothing_window`)

**What:** Moving average window to reduce noise.

**Values:**
- `2` - Minimal smoothing (responsive)
- `3` - Balanced (recommended)
- `4-5` - Heavy smoothing (stable, less sensitive)

**When to use:**
- `2` - Precise, controlled movements
- `3` - General purpose
- `4-5` - Noisy videos or shaky camera

**Example:**
```python
config = DTWConfig(smoothing_window=4)  # More stable
```

---

### 3. Sakoe-Chiba Windowing (`use_window`, `window_percentage`)

**What:** Constrains DTW search to diagonal band (speeds up computation).

**Values:**
- `use_window=False` - No constraint (accurate but slow)
- `use_window=True, window_percentage=0.10` - Tight constraint (fast)
- `use_window=True, window_percentage=0.15` - Balanced (recommended)
- `use_window=True, window_percentage=0.20` - Loose constraint

**When to use:**
- Disable: Short sequences (<100 frames), need maximum accuracy
- 10%: Fast processing, similar speeds expected
- 15%: General purpose (default)
- 20%: Very different speeds possible

**Auto-calculation:** Window only applies to sequences >500 frames.

**Example:**
```python
config = DTWConfig(
    use_window=True,
    window_percentage=0.10  # Tight 10% window
)
```

---

### 4. FastDTW (`use_fastdtw`)

**What:** Approximation algorithm for very long sequences.

**Values:**
- `False` - Use exact DTW (default)
- `True` - Enable FastDTW for sequences >1000 frames

**Requirements:**
```bash
pip install fastdtw
```

**When to use:**
- Videos >90 seconds
- Real-time constraints
- Acceptable accuracy trade-off

**Example:**
```python
config = DTWConfig(
    use_fastdtw=True,
    fastdtw_threshold=500  # Trigger at 500 frames instead of 1000
)
```

---

### 5. Stressed Joint Thresholds

**What:** Minimum deviation to flag a joint as "stressed".

**Default:** `0.25` (normalized units)

**Presets:**
```python
from app.core.config import StressedJointThresholds

# Strict (catch minor deviations)
config.custom_thresholds = StressedJointThresholds.strict()

# Moderate (balanced)
config.custom_thresholds = StressedJointThresholds.moderate()

# Relaxed (only major issues)
config.custom_thresholds = StressedJointThresholds.relaxed()
```

**Custom per-joint:**
```python
config.custom_thresholds = {
    "left_shoulder": 0.15,   # Very sensitive
    "right_shoulder": 0.15,
    "left_elbow": 0.25,      # Normal
    "left_knee": 0.40,       # Less sensitive
}
```

---

### 6. Similarity Scaling (`similarity_scale`)

**What:** Output format for similarity score.

**Values:**
- `"0-1"` - Float between 0 and 1 (default)
- `"0-100"` - Percentage from 0 to 100

**Example:**
```python
config = DTWConfig(similarity_scale="0-100")
# Returns: {"similarity_percentage": 92.5}
```

---

## Preset Configurations

### 1. Precise

**Use case:** Maximum accuracy, detailed analysis

```python
DTWConfig(
    frame_sample_rate=1,      # All frames
    smoothing_window=2,       # Minimal smoothing
    use_window=False,         # No window constraint
    use_fastdtw=False,        # Exact DTW
    stressed_joint_threshold=0.20  # Strict threshold
)
```

**Performance:** Slowest, ~5-10s for 30sec video  
**Accuracy:** Highest

---

### 2. Balanced (Default)

**Use case:** General purpose, good speed/accuracy trade-off

```python
DTWConfig(
    frame_sample_rate=1,      # All frames
    smoothing_window=3,       # Balanced smoothing
    use_window=True,          # 15% window for long sequences
    window_percentage=0.15,
    use_fastdtw=False,        # Exact DTW
    stressed_joint_threshold=0.25  # Standard threshold
)
```

**Performance:** Moderate, ~1-3s for 30sec video  
**Accuracy:** High

---

### 3. Fast

**Use case:** Quick comparison, real-time scenarios

```python
DTWConfig(
    frame_sample_rate=2,      # Every 2nd frame
    smoothing_window=4,       # More smoothing
    use_window=True,          # Tight 10% window
    window_percentage=0.10,
    use_fastdtw=True,         # Enable FastDTW
    stressed_joint_threshold=0.30  # Relaxed threshold
)
```

**Performance:** Fast, <1s for 30sec video  
**Accuracy:** Good

---

### 4. Long Sequences

**Use case:** Videos >60 seconds

```python
DTWConfig(
    frame_sample_rate=3,      # Every 3rd frame
    smoothing_window=5,       # Heavy smoothing
    use_window=True,          # 10% window
    window_percentage=0.10,
    use_fastdtw=True,         # Enable FastDTW
    fastdtw_threshold=500,    # Earlier trigger
    stressed_joint_threshold=0.25
)
```

**Performance:** Fast, ~2-4s for 120sec video  
**Accuracy:** Good

---

## API Usage

### Via Query Parameter

```bash
POST /api/compare?preset=fast
```

### Programmatic Configuration

```python
from app.core.config import DTWConfig, set_dtw_config

# Create custom config
config = DTWConfig(
    frame_sample_rate=2,
    smoothing_window=3,
    use_window=True,
    window_percentage=0.12
)

# Set globally
set_dtw_config(config)

# All subsequent comparisons use this config
```

---

## Performance Optimization

### Decision Tree

```
Video length?
├─ <30 sec
│  ├─ Need maximum accuracy? → preset=precise
│  └─ Otherwise → preset=balanced (default)
│
├─ 30-60 sec
│  ├─ Fast motion? → preset=fast
│  └─ Otherwise → preset=balanced
│
└─ >60 sec → preset=long_sequences
```

### Frame Rate Guidelines

| Video FPS | Motion Speed | Recommended Sample Rate |
|-----------|--------------|-------------------------|
| 30 FPS | Slow | 1 (all frames) |
| 30 FPS | Normal | 1-2 |
| 30 FPS | Fast | 2-3 |
| 60 FPS | Slow | 2 |
| 60 FPS | Normal | 2-3 |
| 60 FPS | Fast | 3-5 |

**Effective FPS after sampling:**
- 30 FPS ÷ 2 = 15 FPS (good for most motions)
- 30 FPS ÷ 3 = 10 FPS (acceptable for slow motions)
- 60 FPS ÷ 3 = 20 FPS (excellent for fast motions)

---

## Stressed Joint Sensitivity

### Threshold Values (Normalized Units)

| Threshold | Sensitivity | Use Case |
|-----------|-------------|----------|
| 0.10-0.15 | Very High | Safety-critical, ergonomic analysis |
| 0.20-0.25 | High | Assembly verification, training |
| 0.30-0.35 | Moderate | General comparison |
| 0.40-0.50 | Low | Rough comparison only |

### Per-Joint Recommendations

**More sensitive (lower thresholds):**
- Shoulders, elbows, wrists (precision matters)
- Use: `0.15 - 0.20`

**Less sensitive (higher thresholds):**
- Knees, ankles (more natural variation)
- Use: `0.30 - 0.40`

---

## Testing & Validation

### Verify Configuration

```python
from app.core.config import get_dtw_config

config = get_dtw_config()
print(f"Sample rate: {config.frame_sample_rate}")
print(f"Smoothing: {config.smoothing_window}")
print(f"Window: {config.use_window}")
```

### Benchmark Different Configs

```python
import time
from app.core.config import DTWPresets, set_dtw_config

presets = ["precise", "balanced", "fast"]
for preset_name in presets:
    config = getattr(DTWPresets, preset_name)()
    set_dtw_config(config)
    
    start = time.time()
    # Run comparison
    result = compare_sessions(...)
    elapsed = time.time() - start
    
    print(f"{preset_name}: {elapsed:.2f}s, similarity={result['similarity']}")
```

---

## Advanced Configuration

### Custom Distance Function

For specialized use cases, modify `pairwise_distances` in `metrics.py`:

```python
def pairwise_distances(A, B):
    # Custom weighted distance
    weights = np.array([...])  # Weight each feature
    return cdist(A * weights, B * weights, metric='euclidean')
```

### Asymmetric Window

For known speed differences:

```python
# User is typically 20% slower
window = int(1.2 * max(n, m))
dtw_result = run_dtw(A, B, window=window)
```

---

## Troubleshooting

### Issue: Comparison is too slow

**Solutions:**
1. Use `preset=fast`
2. Increase `frame_sample_rate` to 2-3
3. Enable windowing: `use_window=True, window_percentage=0.10`
4. Install and enable FastDTW for long sequences

### Issue: Too many stressed joints detected

**Solutions:**
1. Increase threshold: `stressed_joint_threshold=0.35`
2. Use relaxed presets: `StressedJointThresholds.relaxed()`
3. Customize per-joint thresholds

### Issue: Missing important deviations

**Solutions:**
1. Decrease threshold: `stressed_joint_threshold=0.20`
2. Use strict presets: `StressedJointThresholds.strict()`
3. Use `preset=precise` for maximum sensitivity

---

## Best Practices

✅ **DO:**
- Start with `preset=balanced` and adjust as needed
- Use `preset=long_sequences` for videos >60 sec
- Test different configs on sample data
- Document your chosen config in deployment

❌ **DON'T:**
- Use `frame_sample_rate=1` with videos >90 sec (too slow)
- Disable windowing for sequences >1000 frames (very slow)
- Set thresholds <0.10 (too noisy)
- Use `preset=precise` in production without testing performance

---

**For more information, see:**
- `DTW_IMPLEMENTATION.md` - Technical details
- `CHANGELOG.md` - Version history
