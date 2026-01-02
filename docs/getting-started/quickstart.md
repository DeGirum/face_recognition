# Quick Start

Get started with `degirum-face` in under 5 minutes!

## Your First Face Recognition

This example uses built-in demo images and runs on CPU, so it works on any system:

```python
import degirum_face
from degirum_tools import remote_assets

# Demo parameters – change these to try your own images/names
ENROLL_IMAGE = remote_assets.face1
TEST_IMAGE = remote_assets.face2
PERSON_NAME = "Alice"

# 1. Create a face recognizer with default configuration
# By default: uses TFLITE/CPU models running locally
face_recognizer = degirum_face.FaceRecognizer()

# 2. Enroll a person from a reference image
face_recognizer.enroll_image(ENROLL_IMAGE, PERSON_NAME)

# 3. Recognize faces in a test image
print("After enrollment:")
result = face_recognizer.predict(TEST_IMAGE)
for face in result.faces:
    print(face)
```

**Output:**
```
After enrollment:
FaceRecord(identity='Alice', confidence=0.92, bbox=BBox(...), embedding=...)
```

## What Just Happened?

1. **Created a recognizer** - `FaceRecognizer()` sets up face detection and recognition models
2. **Enrolled a face** - `enroll_image()` added "Alice" to the database
3. **Recognized faces** - `predict()` detected and identified faces in the test image

## Common Use Cases

### Batch Process Images

Recognize all faces in a directory:

```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll reference faces
face_recognizer.enroll_image("photos/john.jpg", "John")
face_recognizer.enroll_image("photos/mary.jpg", "Mary")

# Process all images in a folder
results = face_recognizer.predict_batch("group_photos/")

for img_path, result in results:
    print(f"\n{img_path}:")
    for face in result.faces:
        print(f"  {face.identity} ({face.confidence:.2f})")
```

### Real-Time Video Tracking

Track faces in a live video stream:

```python
import degirum_face

# Configure video source and tracking
config = degirum_face.FaceTrackerConfig.from_yaml("config.yaml")
face_tracker = degirum_face.FaceTracker(config)

# Start tracking pipeline
# This opens a video player window and processes the stream
face_tracker.start_face_tracking_pipeline()
```

**config.yaml:**
```yaml
video_source: "rtsp://camera.local/stream"
confirmation_type: "consecutive"
confirmation_frames: 3
```

See [Face Tracker Quick Start](../guides/face-tracker/quickstart.md) for details.

### Search for Similar Faces

Find all photos containing a specific person:

```python
import degirum_face
from pathlib import Path

face_recognizer = degirum_face.FaceRecognizer()

# Enroll the reference photo
face_recognizer.enroll_image("reference/target_person.jpg", "Target")

# Search through all photos
for photo in Path("photo_library/").glob("*.jpg"):
    result = face_recognizer.predict(str(photo))
    
    # Check if target person is in this photo
    for face in result.faces:
        if face.identity == "Target" and face.confidence > 0.85:
            print(f"Found in: {photo}")
            break
```

## Using YAML Configuration

For production use, configure via YAML files:

**config.yaml:**
```yaml
face_detection_model_zoo_url: degirum/public
face_detection_model_name: yolov8n_relu6_face_det--512x512_quant_n2x_orca1_1
inference_host_address: "@local"

landmark_model_zoo_url: degirum/public
landmark_model_name: mobilefacenet_lmks_5pt--112x112_quant_n2x_orca1_1

embedding_model_zoo_url: degirum/public
embedding_model_name: arcface_resnet100--112x112_quant_n2x_orca1_1

face_database_path: "./face_database.lance"
similarity_threshold: 0.50
```

**Python code:**
```python
import degirum_face

# Load configuration from YAML
config = degirum_face.FaceRecognizerConfig.from_yaml("config.yaml")
face_recognizer = degirum_face.FaceRecognizer(config)

# Rest of your code...
face_recognizer.enroll_image("person.jpg", "Alice")
result = face_recognizer.predict("test.jpg")
```

## Next Steps

Choose your path:

### Image Recognition
- **[Face Recognizer Overview](../guides/face-recognizer/overview.md)** - Concepts and architecture
- **[Configuration Guide](../guides/face-recognizer/configuration.md)** - Customize models and thresholds
- **[Methods Reference](../guides/face-recognizer/methods.md)** - All available methods

### Video Tracking
- **[Face Tracker Quick Start](../guides/face-tracker/quickstart.md)** - Real-time tracking
- **[Configuration Guide](../guides/face-tracker/configuration.md)** - Video sources and alerts
- **[Methods Reference](../guides/face-tracker/methods.md)** - Pipeline and batch methods

### Reference
- **[Face Filters](../reference/face-filters.md)** - Age, gender, quality filtering
- **[YAML Configuration](../reference/yaml-config.md)** - Complete YAML schema
- **[Hardware Selection](../guides/face-recognizer/deployment.md)** - Choose the right accelerator

## Examples

Explore working code in the [examples/](../../examples/) folder:

| Example | Description |
|---------|-------------|
| [face_recognition_simple.py](../../examples/face_recognition_simple.py) | Recognize faces in images |
| [face_recognition_enroll.py](../../examples/face_recognition_enroll.py) | Add faces to database |
| [face_tracking_simple.py](../../examples/face_tracking_simple.py) | Real-time face tracking |
| [find_similar_faces.py](../../examples/find_similar_faces.py) | Find similar faces in a collection |
| [group_similar_faces.py](../../examples/group_similar_faces.py) | Group photos by person |
| [Tutorials.ipynb](../../examples/Tutorials.ipynb) | Interactive Jupyter tutorials |
