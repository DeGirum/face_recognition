# Installation

## Requirements

- Python 3.8 or higher
- pip package manager

## Install from PyPI

The simplest way to install `degirum-face`:

```bash
pip install degirum-face
```

This installs the library and all required dependencies.

## Verify Installation

Test that the installation worked:

```python
import degirum_face
print(f"degirum-face version: {degirum_face.__version__}")
```

## Dependencies

`degirum-face` automatically installs these dependencies:

- `degirum` - DeGirum AI inference SDK
- `degirum-tools` - Video processing and utilities
- `numpy` - Numerical computing
- `opencv-python` - Image/video processing

## Hardware-Specific Setup

### CPU Only (Default)

No additional setup needed. The default configuration uses TFLITE/CPU models that work on any system.

### Edge AI Accelerators

For hardware acceleration, install platform-specific drivers:

#### Hailo (HAILORT/HAILO8, HAILORT/HAILO8L)

Follow the [Hailo installation guide](https://docs.degirum.com/pysdk/user-guide-pysdk/installing-hailort-runtime).

#### Intel (OPENVINO/CPU, OPENVINO/GPU, OPENVINO/NPU)

Follow the [OpenVINO installation guide](https://docs.degirum.com/pysdk/user-guide-pysdk/installing-openvino-runtime).

#### NVIDIA (TENSORRT/GPU)

Follow the [TensorRT installation guide](https://docs.degirum.com/pysdk/user-guide-pysdk/installing-tensorrt-runtime).

#### Other Platforms

- **Axelera (AXELERA/METIS)** - [Metis SDK](https://docs.degirum.com/)
- **DEEPX (DEEPX/M1A)** - [DEEPX SDK](https://docs.degirum.com/)
- **Rockchip (RKNN/RK3588)** - [RKNN SDK](https://docs.degirum.com/)
- **Google (TFLITE/EDGETPU)** - [Edge TPU Runtime](https://coral.ai/docs/accelerator/get-started/)
- **DeGirum (N2X/ORCA1)** - [ORCA SDK](https://docs.degirum.com/)

### Cloud Inference (No Local Hardware Needed)

Use `@cloud` inference to try different accelerators without local installation:

```python
import degirum_face

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"  # No local hardware needed!
    ),
    # ... rest of config
)
```

See [Hardware & Deployment](../guides/face-recognizer/deployment.md) for details.

## Next Steps

- **[Quick Start](quickstart.md)** - Run your first face recognition
- **[Basic Concepts](basic-concepts.md)** - Understand key terminology
