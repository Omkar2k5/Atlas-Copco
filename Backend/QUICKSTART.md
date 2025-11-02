# AssemblyFlow Backend - Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web server)
- TensorFlow & MoveNet (pose estimation)
- ChromaDB (vector database)
- OpenCV & NumPy (video processing)

### Step 2: Verify MoveNet Installation

```bash
python test_movenet.py
```

Expected output:
```
✅ All tests passed! MoveNet Thunder is ready.
```

If you see errors, check `MOVENET_MIGRATION.md` for troubleshooting.

### Step 3: Start the Server

```bash
uvicorn app.main:app --reload
```

Server starts at: **http://localhost:8000**

## 📝 Quick API Test

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "vector_database": "connected",
  "embeddings_count": 0,
  "sessions_count": 0
}
```

### Test 2: Interactive API Docs

Open in browser: **http://localhost:8000/docs**

## 🎯 Core Workflows

### Workflow 1: Upload & Process Video

```bash
curl -X POST "http://localhost:8000/api/process-video" \
  -H "Content-Type: multipart/form-data" \
  -F "video=@your_video.mp4"
```

Returns:
- `session_id` - Unique identifier
- `keypoints` - 17 body landmarks per frame
- `embedding` - 256-dim vector for comparison
- `duration_seconds` - Video length

### Workflow 2: Compare Two Sessions (DTW-based)

```bash
curl -X POST "http://localhost:8000/api/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id_reference": "ref-uuid",
    "session_id_user": "user-uuid"
  }'
```

Returns:
- `similarity_score` - 0-1 (higher = more similar) via **DTW alignment**
- `time_difference_seconds` - Timing comparison
- `movement_deviation_vector` - Per-joint differences (aligned frames)
- `stressed_joints` - Problem areas detected
- `recommended_improvements` - Actionable feedback

**New:** Uses Dynamic Time Warping for robust comparison!

### Workflow 3: Retrieve Session

```bash
curl http://localhost:8000/api/session/{session_id}
```

## 🔧 Common Issues

### Issue: "Model not found"

**Solution:**
```bash
# Check model files exist
ls backend/models/

# Should show:
# saved_model.pb
# variables/
```

If missing, re-run: `python download_movenet.py`

### Issue: "Protobuf version conflict"

**Solution:**
```bash
pip install protobuf==4.25.0
```

### Issue: "Video processing is slow"

**Solutions:**
1. **GPU acceleration:**
   ```bash
   pip install tensorflow[and-cuda]
   ```

2. **Process fewer frames:**
   Edit `app/core/pose_model.py`, add frame skipping in `extract_keypoints`

## 📊 Model Information

**MoveNet Thunder:**
- 17 keypoints (nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles)
- Input: 256x256 RGB images
- Output: (y, x, confidence) per keypoint
- Optimized for full-body tracking

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/                 # REST endpoints
│   ├── core/                # Pose model, embedding, metrics
│   ├── db/                  # ChromaDB & JSON storage
│   └── schemas/             # Pydantic models
├── models/                  # MoveNet Thunder model
├── uploads/                 # Uploaded videos (auto-created)
├── session_data/            # JSON session files (auto-created)
├── chroma_db/               # Vector database (auto-created)
└── test_movenet.py          # Integration test
```

## 🎓 Next Steps

1. **Read full docs:** `README.md`
2. **Understand migration:** `MOVENET_MIGRATION.md`
3. **Deploy to production:** Configure CORS, add authentication
4. **Optimize performance:** Enable GPU, tune frame sampling

## 💡 Tips

- **Development:** Use `--reload` flag for auto-restart
- **Production:** Use multiple workers: `--workers 4`
- **Debugging:** Check logs in terminal output
- **API Docs:** Always available at `/docs`

## 📞 Support

Having issues? Check:
1. `README.md` - Full documentation
2. `MOVENET_MIGRATION.md` - Technical details
3. Test script: `python test_movenet.py`

---

**Ready to build? Start the server and open http://localhost:8000/docs** 🚀
