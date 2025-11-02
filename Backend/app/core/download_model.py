"""
Download and cache MoveNet Thunder model from TensorFlow Hub
"""

import tensorflow_hub as hub

print("Downloading MoveNet Thunder model from TensorFlow Hub...")
print("This may take a few minutes on first run...")

model = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/4")

print("✅ MoveNet Thunder model downloaded and cached successfully!")
print("Model will be loaded from cache on subsequent runs.")
