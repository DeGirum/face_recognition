# Installation & Setup

## Prerequisites

- **Python & OS Requirements:** See [DeGirum PySDK Documentation](https://docs.degirum.com/pysdk/installation)
- **DeGirum AI Hub Account:** Create an account at [AI Hub](https://hub.degirum.com/) and set up a workspace with the appropriate permissions to generate licenses for `degirum-face`. See [Workspace Plans](https://docs.degirum.com/ai-hub/workspace-plans) for plan details and [Manage AI Hub Tokens](https://docs.degirum.com/pysdk/user-guide-pysdk/command-line-interface#manage-ai-hub-tokens) for setting up your authentication token
- **Hardware Acceleration (optional):** See [Runtimes & Drivers](https://docs.degirum.com/pysdk/runtimes-and-drivers) for hardware-specific runtime setup

---

## Setup Workflow

Follow these steps to get started with `degirum-face`:

1. **Create AI Hub Account:** Sign up at [AI Hub](https://hub.degirum.com/) if you don't have an account
2. **Set up Workspace:** Create or join a workspace with the appropriate plan (see [Workspace Plans](https://docs.degirum.com/ai-hub/workspace-plans))
3. **Generate Token:** Follow the [token management guide](https://docs.degirum.com/pysdk/user-guide-pysdk/command-line-interface#manage-ai-hub-tokens) to set up authentication
4. **Install Package:** Run `pip install -i https://pkg.degirum.com degirum-face`
5. **(Optional) Install Hardware Drivers:** If using hardware acceleration, set up the required drivers

---

## Installation

DeGirum hosts its own PyPI server for DeGirum packages.

```bash
pip install -i https://pkg.degirum.com degirum-face
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

> **Note:** This demo uses local CPU models and built-in test images for quick verification. For production use with cloud inference, hardware accelerators, or custom images, you'll need to configure your AI Hub token and specify the appropriate inference host and device type. See [Basic Concepts](basic-concepts.md) for more details.
