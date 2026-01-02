# Face Recognizer Overview

## What is FaceRecognizer?

`FaceRecognizer` is designed for **batch image processing** and **static photo recognition**. It processes individual images or collections of images, detecting and identifying faces without temporal awareness (no tracking across frames).

## When to Use FaceRecognizer

Choose `FaceRecognizer` when you need to:
- Process photo albums or image collections
- Run one-time batch recognition tasks
- Build a face database from images
- Implement simple recognize-and-done workflows
- Work with static images rather than video

**For video streams or real-time tracking**, use [FaceTracker](../face-tracker/quickstart.md) instead.

## How It Works

Every face recognition operation follows this pipeline:

```
┌─────────────┐     ┌──────────┐     ┌───────────┐     ┌──────────────┐
│ Input Image │ ──> │  Detect  │ ──> │   Align   │ ──> │   Embedding  │
│             │     │  Faces   │     │ & Extract │     │  Extraction  │
└─────────────┘     └──────────┘     └───────────┘     └──────────────┘
                                                                │
                                                                v
                                                        ┌──────────────┐
                                                        │   Database   │
                                                        │   Search &   │
                                                        │    Match     │
                                                        └──────────────┘
```

### Pipeline Stages

1. **Face Detection** - Locates all faces in the image (YOLOv8-based)
2. **Landmark Detection & Alignment** - Finds facial keypoints and standardizes pose
3. **Embedding Extraction** - Converts aligned face to 512-D vector (ArcFace ResNet100)
4. **Database Search** - Matches embedding against enrolled faces using cosine similarity

## Core Concepts

### FaceRecognizerConfig

All configuration is done through a `FaceRecognizerConfig` object:

```python
import degirum_face

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,   # Which detection model
    face_embedding_model_spec=embedding_spec,  # Which embedding model
    db_path="./face_db.lance",                 # Where to store faces
    cosine_similarity_threshold=0.6,           # Matching strictness
    face_filters=filter_config,                # Quality filters (optional)
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

See [Configuration Guide](configuration.md) for complete details.

### Default Configuration

When you create `FaceRecognizer()` without arguments, it uses sensible defaults:

```python
# These are equivalent:
face_recognizer = degirum_face.FaceRecognizer()

# Behind the scenes:
default_config = degirum_face.FaceRecognizerConfig()  # Uses all defaults
face_recognizer = degirum_face.FaceRecognizer(default_config)
```

**Default settings:**
- **Hardware:** `TFLITE/CPU` (works on any machine)
- **Inference location:** `@local` (runs on your machine)
- **Database:** `./face_reid_db.lance`
- **Similarity threshold:** `0.6` (balanced accuracy)

This is perfect for getting started, but production deployments will want custom configurations.

### Face Database

Enrolled faces are stored in a LanceDB vector database:

```python
config = degirum_face.FaceRecognizerConfig(
    db_path="./my_faces.lance"  # LanceDB file
)
```

The database contains:
- **Face embeddings** (512-D vectors)
- **Person identities** (names/IDs)
- **Metadata** (enrollment timestamps, etc.)

### Similarity Threshold

Controls how strict matching is:

```python
config = degirum_face.FaceRecognizerConfig(
    cosine_similarity_threshold=0.50  # 50% similarity required
)
```

- **Higher (0.60-0.80):** Stricter, fewer false positives
- **Lower (0.30-0.50):** More lenient, may match similar-looking people
- **Recommended:** Start with 0.50, tune based on your use case

### Face Records

All results are returned as `FaceRecord` objects:

```python
result = face_recognizer.predict("photo.jpg")

for face in result.faces:
    print(f"Identity: {face.attributes}")        # Name or None
    print(f"Confidence: {face.similarity_score}") # 0.0-1.0
    print(f"Bounding Box: {face.bbox}")          # [x1, y1, x2, y2]
    print(f"Embedding: {face.embeddings}")       # 512-D vector
```

## Typical Workflows

### 1. Simple Recognition

Enroll a few people and recognize them in photos:

```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll known faces
face_recognizer.enroll_image("alice.jpg", "Alice")
face_recognizer.enroll_image("bob.jpg", "Bob")

# Recognize faces in new photos
result = face_recognizer.predict("group_photo.jpg")

for face in result.faces:
    if face.attributes:
        print(f"Found: {face.attributes}")
    else:
        print("Unknown person")
```

### 2. Batch Photo Processing

Process an entire photo library:

```python
import degirum_face
from pathlib import Path

face_recognizer = degirum_face.FaceRecognizer()

# Enroll reference faces
face_recognizer.enroll_image("alice_ref.jpg", "Alice")
face_recognizer.enroll_image("bob_ref.jpg", "Bob")

# Process all photos in a directory
photo_dir = Path("photo_library/")
image_paths = list(photo_dir.glob("*.jpg"))

for result in face_recognizer.predict_batch(iter(image_paths)):
    for face in result.faces:
        if face.attributes:
            print(f"{result.image_path}: {face.attributes}")
```

### 3. Find Similar Faces

Search for specific people across a collection:

```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll target person
face_recognizer.enroll_image("target.jpg", "Target Person")

# Search through all photos
matches = []
for photo in photo_library:
    result = face_recognizer.predict(photo)
    
    for face in result.faces:
        if face.attributes == "Target Person" and face.similarity_score > 0.85:
            matches.append((photo, face.similarity_score))
            break

# Print results sorted by confidence
for photo, score in sorted(matches, key=lambda x: x[1], reverse=True):
    print(f"{photo}: {score:.2f}")
```

## Next Steps

- **[Configuration Guide](configuration.md)** - Customize models, thresholds, and filters
- **[Methods Reference](methods.md)** - Complete API documentation
- **[Deployment Guide](deployment.md)** - Hardware selection and production setup
- **[Face Filters Reference](../../reference/face-filters.md)** - Quality filtering options
