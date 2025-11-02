# AssemblyFlow - AI-Powered Motion Analysis System

AssemblyFlow is a comprehensive motion analysis and pose comparison system that uses **MoveNet** for pose estimation and **Dynamic Time Warping (DTW)** for sequence alignment. It helps analyze human movement patterns, compare motion sequences, and provide actionable feedback.

## 🌟 Features

- **Video Upload & Processing**: Upload videos and extract pose keypoints using MoveNet
- **Motion Embeddings**: Generate 42-dimensional feature vectors from pose sequences
- **DTW-based Comparison**: Compare two motion sequences with time-aligned analysis
- **Stressed Joint Detection**: Automatically identify joints under stress
- **Actionable Recommendations**: Get specific improvement suggestions
- **Session Management**: Store and retrieve analysis sessions
- **Real-time Progress**: Track upload and processing progress
- **Modern UI**: Clean, responsive Next.js frontend

## 🏗️ Architecture

```
AssemblyFlow/
├── backend/           # FastAPI backend with MoveNet + DTW
│   ├── app/
│   │   ├── api/       # API endpoints (process, compare, session)
│   │   ├── core/      # Core logic (embedding, metrics, pose model)
│   │   ├── db/        # Storage (vector DB, session storage)
│   │   └── main.py    # FastAPI app entry point
│   ├── models/        # MoveNet model files
│   └── requirements.txt
│
└── Frontend/          # Next.js 16 frontend
    ├── app/
    │   ├── (main)/    # Main routes (upload, compare, analyze, history)
    │   └── page.tsx   # Landing page
    ├── components/    # React components
    ├── lib/
    │   ├── api-client.ts      # API client with axios
    │   └── hooks/use-api.ts   # React hooks for API calls
    └── types/         # TypeScript interfaces
```

## 📋 Prerequisites

### Backend Requirements
- **Python**: 3.9 or higher
- **pip**: Python package manager
- **TensorFlow**: 2.x (installed via requirements.txt)

### Frontend Requirements
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
cd "C:\Projects\Sponspered Atlas Copco"
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `tensorflow` - MoveNet pose estimation
- `opencv-python` - Video processing
- `numpy` - Numerical computations
- `scipy` - DTW distance computations
- `chromadb` - Vector database
- `python-multipart` - File upload support

#### Download MoveNet Model

The MoveNet model will be automatically downloaded on first run. Ensure you have internet connectivity.

**Manual download (optional):**
```bash
# Model will be saved to: backend/models/movenet_thunder.tflite
```

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd Frontend
npm install
```

**Key Dependencies:**
- `next` - React framework
- `react` & `react-dom` - UI library
- `axios` - HTTP client
- `typescript` - Type safety
- `tailwindcss` - Styling

#### Configure Environment Variables

Create a `.env.local` file in the `Frontend` directory:

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## ▶️ Running the Application

You need to run **both backend and frontend** simultaneously in separate terminal windows.

### Terminal 1: Start Backend

```bash
cd "C:\Projects\Sponspered Atlas Copco\backend"
python -m uvicorn app.main:app --reload
```

**Expected Output:**
```
Loading pose estimation model...
✓ Pose model loaded
Connecting to vector database...
✓ Vector database connected (0 embeddings)
Initializing session storage...
✓ Session storage ready (0 sessions)

🚀 AssemblyFlow API is ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Backend will be available at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### Terminal 2: Start Frontend

```bash
cd "C:\Projects\Sponspered Atlas Copco\Frontend"
npm run dev
```

**Expected Output:**
```
▲ Next.js 16.0.0 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000

✓ Ready in 3s
```

**Frontend will be available at:** `http://localhost:3000`

## 🎯 Usage Guide

### 1. **Home Page** (`/`)
- Check backend connection status
- Navigate to different sections
- View technology stack

### 2. **Upload & Analyze** (`/upload`)
- Click to upload a video file (MP4, AVI, MOV)
- Watch real-time upload progress
- Video is processed using MoveNet
- Automatically redirected to analysis page
- Session ID is generated and stored

### 3. **Compare Sessions** (`/compare`)
- Select two previously uploaded sessions
- Choose DTW preset:
  - **Balanced** (default) - Good speed/accuracy balance
  - **Precise** - Higher accuracy, slower
  - **Fast** - Quick results, lower precision
  - **Long Sequences** - Optimized for videos >30s
- Click "Compare" to run DTW alignment
- View results:
  - Similarity score
  - Time difference
  - Stressed joints
  - Actionable recommendations

### 4. **Session History** (`/history`)
- View all uploaded sessions
- Session details (ID, timestamp, duration)
- Delete old sessions

### 5. **Analysis Details** (`/analyze/[sessionId]`)
- View individual session analysis
- Keypoints visualization
- Motion embeddings
- Session metrics

## 🔧 API Endpoints

### Process Video
```http
POST /api/process-video
Content-Type: multipart/form-data

Response:
{
  "session_id": "uuid",
  "keypoints": [[[x, y, confidence], ...], ...],
  "embedding": [float, ...],
  "duration_seconds": float
}
```

### Compare Sessions
```http
POST /api/compare?preset=balanced
Content-Type: application/json

Body:
{
  "session_id_reference": "uuid1",
  "session_id_user": "uuid2"
}

Response:
{
  "similarity_score": float,
  "time_difference_seconds": float,
  "stressed_joints": ["joint1", "joint2"],
  "recommended_improvements": ["tip1", "tip2"],
  "method": "dtw_classic"
}
```

### Get Session
```http
GET /api/session/{session_id}

Response:
{
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "keypoints": [...],
  "embedding": [...],
  "duration_seconds": float
}
```

### List Sessions
```http
GET /api/sessions

Response:
{
  "sessions": [
    {
      "session_id": "uuid",
      "timestamp": "ISO8601",
      "duration_seconds": float
    }
  ]
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Type Checking
```bash
cd Frontend
npm run type-check
```

## 📊 DTW Presets Explained

| Preset | Window | Step Pattern | Best For | Speed |
|--------|--------|--------------|----------|-------|
| **Balanced** | 15% | Asymmetric | General use | Medium |
| **Precise** | 20% | Asymmetric | High accuracy | Slow |
| **Fast** | 10% | Symmetric | Quick checks | Fast |
| **Long Sequences** | 5% | Asymmetric | Videos >30s | Medium |

## 🛠️ Troubleshooting

### Backend Won't Start

**Issue:** `ModuleNotFoundError: No module named 'app'`
```bash
# Make sure you're in the backend directory
cd backend
python -m uvicorn app.main:app --reload
```

**Issue:** `TensorFlow not found`
```bash
pip install tensorflow
```

### Frontend Connection Error

**Issue:** `Backend: offline` on landing page

✅ **Check backend is running:**
```bash
# Should return status 200
curl http://localhost:8000/health
```

✅ **Check CORS settings:**
- Backend should allow `http://localhost:3000`
- Check `backend/app/main.py` CORS middleware

**Issue:** `ECONNREFUSED`
```bash
# Verify API URL in .env.local
cat Frontend/.env.local
# Should be: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Video Processing Fails

**Issue:** `Failed to process video`

- Check video format (MP4, AVI, MOV supported)
- Ensure video has visible people
- Check backend logs for detailed errors
- Verify MoveNet model is loaded

## 📁 Project Structure Details

### Backend Core Modules

- **`core/pose_model.py`** - MoveNet model loading and inference
- **`core/embedding.py`** - 42D feature extraction (angles + positions)
- **`core/metrics.py`** - DTW implementation with path reconstruction
- **`api/process_video.py`** - Video upload and processing endpoint
- **`api/compare.py`** - DTW comparison endpoint
- **`api/session.py`** - Session CRUD operations
- **`db/vector_db.py`** - ChromaDB for embedding storage
- **`db/storage.py`** - JSON-based session storage

### Frontend Key Files

- **`lib/api-client.ts`** - Axios-based API client
- **`lib/hooks/use-api.ts`** - React hooks (useProcessVideo, useCompare, etc.)
- **`app/page.tsx`** - Landing page with health check
- **`app/(main)/upload/page.tsx`** - Video upload with progress
- **`app/(main)/compare/page.tsx`** - Session comparison with DTW
- **`types/index.ts`** - TypeScript interfaces

## 🔐 Security Notes

- CORS is configured for development (`localhost:3000`)
- Update CORS origins for production deployment
- No authentication implemented (add as needed)
- Session storage is local (not production-ready)

## 📝 License

[Specify your license here]

## 👥 Contributors

- Your Name / Team

## 🙏 Acknowledgments

- **MoveNet** by Google for pose estimation
- **FastAPI** for the awesome web framework
- **Next.js** for the React framework
- **DTW** algorithm for sequence alignment

---

**Need Help?** Check the documentation in `backend/docs/` or open an issue.

**Happy Motion Analysis! 🎉**
