# AssemblyFlow Backend

Motion analysis and human pose comparison system backend built with FastAPI.

## Overview

AssemblyFlow analyzes human movement from video, extracts pose keypoints using MediaPipe, generates vector embeddings, and provides detailed comparison metrics between different executions.

## Features

- **Video Processing**: Upload videos and extract pose keypoints
- **Pose Estimation**: MoveNet Thunder-based pose detection with 17 landmarks
- **Embedding Generation**: Convert variable-length sequences to fixed-length vectors
- **Vector Database**: ChromaDB for efficient similarity search
- **Comparison Metrics**: Similarity scores, time differences, movement deviations
- **Ergonomic Analysis**: Detect stressed joints and provide recommendations

## Architecture

```
backend/
├── app/
│   ├── main.py                # FastAPI application entry point
│   ├── api/
│   │   ├── process_video.py   # Video upload & processing endpoint
│   │   ├── compare.py         # Session comparison endpoint
│   │   └── session.py         # Session management endpoints
│   ├── core/
│   │   ├── pose_model.py      # MediaPipe pose estimation
│   │   ├── embedding.py       # Embedding generation
│   │   └── metrics.py         # Comparison metrics calculation
│   ├── db/
│   │   ├── vector_db.py       # ChromaDB vector database
│   │   └── storage.py         # JSON session storage
│   └── schemas/
│       ├── pose.py            # Pose processing schemas
│       ├── compare.py         # Comparison schemas
│       └── session.py         # Session schemas
└── requirements.txt
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

1. **Clone the repository** (if applicable):
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Process Video

**POST** `/api/process-video`

Upload a video file to extract pose keypoints and generate embeddings.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `video` (file)

**Response:**
```json
{
  "session_id": "uuid",
  "keypoints": [[[x, y, confidence]]],
  "embedding": [0.1, 0.2, ...],
  "step_segments": null,
  "duration_seconds": 15.5
}
```

### 2. Compare Sessions

**POST** `/api/compare`

Compare two pose execution sessions.

**Request:**
```json
{
  "session_id_reference": "uuid-reference",
  "session_id_user": "uuid-user"
}
```

**Response:**
```json
{
  "similarity_score": 0.85,
  "time_difference_seconds": -2.3,
  "movement_deviation_vector": [0.1, 0.2, ...],
  "stressed_joints": ["left_shoulder", "neck"],
  "recommended_improvements": [
    "Keep your head aligned with your spine to reduce neck strain"
  ]
}
```

### 3. Get Session

**GET** `/api/session/{session_id}`

Retrieve complete session data by ID.

**Response:**
```json
{
  "session_id": "uuid",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "user_id": "user123",
  "duration_seconds": 15.5,
  "keypoints": [[[x, y, confidence]]],
  "embedding": [0.1, 0.2, ...]
}
```

### 4. List Sessions

**GET** `/api/sessions?user_id={user_id}`

List all sessions with optional user filtering.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "user_id": "user123",
      "duration_seconds": 15.5
    }
  ]
}
```

### 5. Delete Session

**DELETE** `/api/session/{session_id}`

Delete a session from storage and vector database.

**Response:**
```json
{
  "message": "Session {session_id} deleted successfully"
}
```

## Data Storage

### Session Storage
- Location: `./session_data/`
- Format: JSON files named `{session_id}.json`
- Contains: keypoints, embeddings, metadata

### Vector Database
- Location: `./chroma_db/`
- Engine: ChromaDB (DuckDB + Parquet)
- Contains: embeddings for similarity search

### Uploaded Videos
- Location: `./uploads/`
- Format: Original video files with timestamped names

## Configuration

### Pose Model Settings

The backend uses **MoveNet Thunder** for pose estimation:
- 17 keypoints (vs MediaPipe's 33)
- More accurate for full-body movements
- Loaded from local SavedModel in `backend/models/`

Model input size: 256x256 pixels

### Embedding Dimension

Edit `app/core/embedding.py`:
```python
target_size = 256  # Change embedding dimension
```

### CORS Settings

Edit `app/main.py`:
```python
allow_origins=["http://localhost:3000"]  # Restrict origins
```

## Testing

### Test Video Upload

```bash
curl -X POST "http://localhost:8000/api/process-video" \
  -H "Content-Type: multipart/form-data" \
  -F "video=@test_video.mp4"
```

### Test Comparison

```bash
curl -X POST "http://localhost:8000/api/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id_reference": "reference-uuid",
    "session_id_user": "user-uuid"
  }'
```

## Troubleshooting

### TensorFlow / MoveNet Issues

If TensorFlow fails to load the model:
```bash
# Ensure model files are in backend/models/
ls backend/models/

# Should show: saved_model.pb, variables/
```

If you get protobuf errors, downgrade:
```bash
pip install protobuf==4.25.0
```

### ChromaDB Errors

If ChromaDB throws errors, delete the database and restart:
```bash
rm -rf chroma_db/
```

### Video Processing Errors

Ensure video codecs are supported:
- Supported formats: MP4, AVI, MOV, MKV, WEBM
- If issues persist, try re-encoding video with H.264 codec

## Performance Optimization

### For Faster Processing

1. **GPU Acceleration**: MoveNet benefits significantly from GPU
   ```bash
   # Install TensorFlow with GPU support
   pip install tensorflow[and-cuda]
   ```

2. **Process fewer frames**: Sample every Nth frame
   ```python
   # In extract_keypoints method
   frame_count = 0
   while cap.isOpened():
       ret, frame = cap.read()
       if not ret:
           break
       frame_count += 1
       if frame_count % 2 != 0:  # Process every 2nd frame
           continue
   ```

3. **Reduce input size**: Use MoveNet Lightning (192x192) instead of Thunder (256x256)
   - Faster but slightly less accurate

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Real-time video streaming support
- [ ] Step segmentation implementation
- [ ] ML-based movement quality scoring
- [ ] Multi-person pose tracking
- [ ] Export reports as PDF

## License

[Add your license here]

## Support

For issues and questions, please contact [your contact information].
