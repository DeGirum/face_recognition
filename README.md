# Face Recognition Examples using `degirum-face`

This repository demonstrates practical usage of the `degirum-face` Python package for face detection, recognition, and tracking. Here you'll find ready-to-run scripts and a web app that show how to:
- Detect and recognize faces in images and video
- Build and search a face database
- Track faces in real time
- Easily enroll new faces


## What is `degirum-face`?
`degirum-face` is a high-performance, easy-to-use Python library for face recognition and tracking. It offers:
- **Fast and efficient** face detection, alignment, embedding extraction, and recognition for images, video files, and live streams
- **Multi-hardware support**: Works on CPU, GPU, and a wide range of edge AI accelerators:  
  - **Hailo** (HAILORT/HAILO8, HAILORT/HAILO8L)
  - **Axelera** (AXELERA/METIS)
  - **DEEPX** (DEEPX/M1A)
  - **Intel** (OPENVINO/CPU, OPENVINO/GPU, OPENVINO/NPU)
  - **NVIDIA** (TENSORRT/GPU)
  - **Rockchip** (RKNN/RK3588) 
  - **Google** (TFLITE/EDGETPU)
  - **DeGirum** (N2X/ORCA1)
- **Simple APIs**: Minimal code to detect, enroll, and recognize faces, with easy batch processing
- **Flexible configuration**: YAML or Python config for models, thresholds, and database paths
- **Robust database and real-time tracking**: Face re-identification, database search, event notification, and easy batch enrollment
- **Production-ready**: Used in real-world applications

---


## Installation

Install from PyPI:

```bash
pip install degirum-face
```

## Quickstart

**Try it now** — this example uses built-in demo images and runs on CPU (TFLITE/CPU) locally, so it works on any system:

```python
import degirum_face
from degirum_tools import remote_assets

# Demo parameters – change these to try your own images / names
ENROLL_IMAGE = remote_assets.face1
TEST_IMAGE = remote_assets.face2
PERSON_NAME = "Alice"

# 1. Create a face recognizer with default configuration
# By default: uses TFLITE/CPU models running locally (@local inference host)
face_recognizer = degirum_face.FaceRecognizer()

# 2. Enroll a person from a reference image
face_recognizer.enroll_image(ENROLL_IMAGE, PERSON_NAME)

# 3. Recognize faces in a test image
print("After enrollment:")
result = face_recognizer.predict(TEST_IMAGE)
for face in result.faces:
    print(face)
```

## Examples & Applications

| Example | Description |
|---------|-------------|
| [face_recognition_simple.py](examples/face_recognition_simple.py) | Recognize faces in images |
| [face_recognition_enroll.py](examples/face_recognition_enroll.py) | Add faces to database |
| [face_tracking_simple.py](examples/face_tracking_simple.py) | Real-time face tracking |
| [find_similar_faces.py](examples/find_similar_faces.py) | Find similar faces in a collection |
| [group_similar_faces.py](examples/group_similar_faces.py) | Group photos by person |
| [Tutorials.ipynb](examples/Tutorials.ipynb) | Interactive Jupyter notebook tutorials |
| [Web App](apps/face_tracking_web_app) | Full-featured web UI for tracking + NVR |

See [examples/](examples) for all available examples.

## Documentation

Complete documentation is in the [`docs/`](docs/) folder:

### FaceRecognizer (Image/Batch Processing)
- **[FaceRecognizer Guide](docs/face_recognizer.md)** - Complete guide for image and batch processing
  - Understanding the defaults
  - Configuration anatomy
  - Methods (enroll, predict, batch processing)
  - Deployment options (cloud, local, remote)
  - Hardware selection (12+ accelerator platforms)
  - YAML configuration
  - Face filtering

### FaceTracker (Video Surveillance)
- **[Quick Start](docs/face_tracker_quickstart.md)** - Get started with video tracking quickly
- **[Configuration Reference](docs/face_tracker_config.md)** - All configuration options
- **[Methods Guide](docs/face_tracker_methods.md)** - All methods with workflows and examples

### Additional Guides
- **[FaceClipManager](docs/face_clip_manager.md)** - Manage video clips in object storage
- **[Documentation Index](docs/README.md)** - Complete documentation index with quick navigation

### Examples
- [examples/](examples) - Ready-to-run code samples

## License
See [LICENSE](LICENSE#L1) for license details.

