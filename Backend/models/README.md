# MoveNet Model Files

Downloaded from: google/movenet
Source path: C:\Users\Omkar\.cache\kagglehub\models\google\movenet\tensorFlow2\singlepose-thunder\4

## Files
- saved_model.pb
- variables.data-00000-of-00001
- variables.index

## Usage

This model is currently set up for TensorFlow.js format.
The backend uses MediaPipe for pose estimation, which is already configured.

To use MoveNet instead of MediaPipe:
1. Install tensorflow or tensorflow-lite
2. Update `app/core/pose_model.py` to load this model
3. Modify the inference code accordingly
