# Installation & Setup

## Prerequisites

- **Python & OS Requirements:** See [DeGirum PySDK Documentation](https://docs.degirum.com/pysdk/installation)
- **DeGirum AI Hub Account:** You need a workspace with permissions to generate a license for `degirum-face`
- **Hardware Acceleration (optional):** See [Runtimes & Drivers](https://docs.degirum.com/pysdk/runtimes-and-drivers) for hardware-specific runtime setup

---

## Installation

Install from PyPI:

```bash
pip install degirum-face
```

---

## Verify Installation

Quick test using built-in demo images and CPU models:

```python
import degirum_face
from degirum_tools import remote_assets

# Demo parameters
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

This runs on any system without additional setup.
