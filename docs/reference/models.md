# Face Recognition Models

## Overview

`degirum-face` uses two types of AI models for face recognition: **face detection models** and **face embedding models**. Both are optimized and compiled for a wide range of hardware platforms through the DeGirum model registry.

> **Important:** The `degirum_face` library provides code and pipelines for face recognition workflows. Model licensing is separate from the `degirum_face` library licensing. See the license section under each model type for specific licensing requirements.

## Face Detection Models

### Purpose

Face detection models locate faces in images and identify 5 facial keypoints (landmarks):
- Left eye
- Right eye  
- Nose
- Left mouth corner
- Right mouth corner

These keypoints enable face alignment - a critical step for accurate embedding extraction.

### License

Face detection models are trained by DeGirum and can be used commercially when users license the `degirum-face` package. Contact DeGirum for licensing information.

### Model Details

- **Training:** All face detection models are trained by DeGirum
- **Output:** Bounding boxes + 5 keypoints per detected face
- **Compilation:** Models are compiled and optimized for all supported hardware platforms:
  - Hailo (HAILORT/HAILO8, HAILORT/HAILO8L)
  - Axelera (AXELERA/METIS)
  - DEEPX (DEEPX/M1A)
  - Intel (OPENVINO/CPU, OPENVINO/GPU, OPENVINO/NPU)
  - NVIDIA (TENSORRT/GPU)
  - Rockchip (RKNN/RK3588)
  - Google (TFLITE/EDGETPU)
  - DeGirum (N2X/ORCA1)

### Usage

Detection models are automatically selected from the model registry based on your hardware configuration:

```python
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
```

## Face Embedding Models

### Purpose

Face embedding models convert aligned face images into numerical vectors (embeddings) that capture unique facial features. These embeddings enable face matching and identification.

### License

The ONNX file for the face embedding model is from the [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo) and is licensed under the MIT license. See [THIRD-PARTY-LICENSES.md](../../THIRD-PARTY-LICENSES.md) for the complete license text and copyright notice.

### Model Details

- **Architecture:** ArcFace MobileFacenet
- **Source:** ONNX model from [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_face_recognition.rst)
- **Compilation:** DeGirum compiled the ONNX model for all supported hardware platforms
- **Output:** 512-dimensional embedding vector per face

### ArcFace Model

The ArcFace (Additive Angular Margin Loss) model is a state-of-the-art face recognition architecture that:
- Uses MobileFacenet backbone for feature extraction
- Produces highly discriminative face embeddings
- Achieves excellent accuracy on face recognition benchmarks
- Generalizes well across different lighting conditions, poses, and demographics

### Usage

Embedding models are automatically selected from the model registry:

```python
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
```

## Model Registry

The DeGirum model registry automatically selects the optimal model for your hardware platform. This eliminates the need to manually choose models or tune parameters.

**Benefits:**
- Pre-optimized models for each hardware platform
- Automatic model selection based on device type
- Consistent performance across different hardware
- Simplified configuration

**Accessing the registry:**

```python
# List all supported hardware platforms
supported_hw = degirum_face.model_registry.get_hardware()

# Get available hardware on cloud or local
available_hw = degirum_face.get_system_hw("@cloud")

# Find compatible hardware you can use now
compatible_hw = degirum_face.get_compatible_hw("@cloud")
```

## Custom Models

While the model registry provides optimized models for all supported platforms, you can also use custom models by creating `ModelSpec` objects directly. This is useful for:
- Using proprietary face detection models
- Testing alternative embedding architectures
- Integrating domain-specific models

See [ModelSpec Documentation](https://docs.degirum.com/degirum-tools/model_registry#modelspec) for details on using custom models.

## Model Performance

Performance varies by hardware platform and model complexity. Key factors:

**Face Detection:**
- Input resolution impacts speed and accuracy
- Higher resolution = better small face detection, slower processing
- Typical throughput: 10-100+ FPS depending on hardware

**Face Embedding:**
- Fixed input size (typically 112×112 pixels)
- Extraction time: 1-50ms per face depending on hardware
- Batch processing improves throughput for multiple faces

For production deployments, test with your specific hardware and video resolution to determine optimal settings.

## Acknowledgments

We gratefully acknowledge [Hailo](https://hailo.ai/) for providing the ArcFace MobileFacenet ONNX model through the [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo). This model enables high-quality face recognition capabilities in `degirum-face`. DeGirum has compiled and optimized this model for all supported hardware platforms to ensure consistent performance across different deployment scenarios.
