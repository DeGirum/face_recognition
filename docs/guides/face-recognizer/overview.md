# FaceRecognizer Overview

Complete guide to understanding when and how to use `FaceRecognizer` for face recognition tasks.

## What is FaceRecognizer?

`FaceRecognizer` processes images and video frames independently without temporal tracking. It detects and identifies faces in single images, image batches, or video streams (frame-by-frame via `predict_batch()`).

## When to Use FaceRecognizer

Choose `FaceRecognizer` when you need to:
- Process photo albums or image collections
- Analyze video files frame-by-frame without temporal tracking
- Run batch recognition on multiple images or video streams
- Build a face database from images
- Work without real-time tracking requirements

**For video with persistent face tracking**, use [FaceTracker](../face-tracker/overview.md) instead - it maintains face identities across frames and supports real-time alerts.

## Core Concepts

### Configuration

All settings are controlled through `FaceRecognizerConfig`:

```python
import degirum_face

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,   # Detection model
    face_embedding_model_spec=embedding_spec,  # Embedding model
    db_path="./face_db.lance",                 # Database location
    cosine_similarity_threshold=0.6,           # Match threshold
)

face_recognizer = degirum_face.FaceRecognizer(config)
```
See [Configuration Guide](configuration.md) for all options.

## Methods

`FaceRecognizer` provides methods for enrollment, prediction, and database management:

- **[enroll_image()](methods.md#enroll_image)** / **[enroll_batch()](methods.md#enroll_batch)** - Add faces to database
- **[predict()](methods.md#predict)** / **[predict_batch()](methods.md#predict_batch)** - Recognize faces in images/video

See [Methods Reference](methods.md) for complete API documentation with examples.

