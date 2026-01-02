# Face Recognizer Configuration

Complete guide to configuring `FaceRecognizer` for your specific hardware, deployment environment, and use case.

## FaceRecognizerConfig Anatomy

`FaceRecognizer` is configured entirely through a `FaceRecognizerConfig` object with these components:

```python
import degirum_face

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,   # 1. Detection model
    face_embedding_model_spec=embedding_spec,  # 2. Embedding model
    db_path="./face_db.lance",                 # 3. Database path
    cosine_similarity_threshold=0.6,           # 4. Matching threshold
    face_filters=filter_config,                # 5. Quality filters (optional)
)
```

### 1. Face Detection Model Spec (Required)

Specifies which model detects faces and their bounding boxes.

```python
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
```

### 2. Face Embedding Model Spec (Required)

Specifies which model extracts face embeddings for matching.

```python
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
```

### 3. Database Path (Required)

Where to store enrolled face embeddings (LanceDB file).

```python
db_path="./face_reid_db.lance"
```

### 4. Similarity Threshold (Required)

Minimum cosine similarity (0.0-1.0) to consider two faces a match.

```python
cosine_similarity_threshold=0.6  # Higher = stricter
```

### 5. Face Filters (Optional)

Quality gates to skip low-quality detections. See [Face Filters Reference](../../reference/face-filters.md).

```python
face_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=50
)
```

## Model Specs Explained

A `ModelSpec` tells `degirum-face` **which model** to load and **where to run it**.

### Helper Functions

Use these helpers instead of creating `ModelSpec` objects manually:

```python
import degirum_face

# Get optimized detection model for your hardware
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)

# Get optimized embedding model for your hardware
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
```

These functions automatically select the best models from the `degirum-face` model registry.

### Parameters

- **`device_type`** - Hardware accelerator to use:
  - `TFLITE/CPU` - CPU only (default, works everywhere)
  - `HAILORT/HAILO8` - Hailo-8 accelerator
  - `OPENVINO/CPU`, `OPENVINO/NPU`, `OPENVINO/GPU` - Intel platforms
  - `TENSORRT/GPU` - NVIDIA GPU
  - `N2X/ORCA1` - DeGirum ORCA
  - See [Deployment Guide](deployment.md) for all options

- **`inference_host_address`** - Where to run:
  - `@local` - Local machine
  - `@cloud` - DeGirum AI Hub
  - `192.168.1.100:8778` - Remote server

## Configuration Examples

### Basic - Default Configuration

```python
import degirum_face

# Uses all defaults: TFLITE/CPU running locally
face_recognizer = degirum_face.FaceRecognizer()
```

Equivalent to:

```python
config = degirum_face.FaceRecognizerConfig()
face_recognizer = degirum_face.FaceRecognizer(config)
```

**Defaults:**
- Hardware: `TFLITE/CPU`
- Inference: `@local`
- Database: `./face_reid_db.lance`
- Threshold: `0.6`

### Cloud Experimentation

Try different hardware without local setup:

```python
import degirum_face

# Test Hailo-8 on cloud
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,
    face_embedding_model_spec=embedding_spec,
    db_path="./face_db_hailo8.lance",
    cosine_similarity_threshold=0.6,
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

### Local Edge Deployment

Run on local Hailo-8 accelerator:

```python
import degirum_face

# Local Hailo-8
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@local"  # Local hardware
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@local"
)

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,
    face_embedding_model_spec=embedding_spec,
    db_path="./face_db_hailo8.lance",
    cosine_similarity_threshold=0.6,
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

### Remote Inference Server

Connect to dedicated AI server:

```python
import degirum_face

# Remote NVIDIA GPU server
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="TENSORRT/GPU",
    inference_host_address="192.168.1.100:8778"
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="TENSORRT/GPU",
    inference_host_address="192.168.1.100:8778"
)

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,
    face_embedding_model_spec=embedding_spec,
    db_path="./face_db_tensorrt.lance",
    cosine_similarity_threshold=0.6,
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

### With Face Filters

Add quality filtering:

```python
import degirum_face

# Create filter configuration
filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=60,
    enable_frontal_filter=True,
    enable_shift_filter=True,
)

# Apply filters in config
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec("TFLITE/CPU"),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec("TFLITE/CPU"),
    db_path="./face_db.lance",
    cosine_similarity_threshold=0.6,
    face_filters=filters,
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

## YAML Configuration

Store configuration in YAML files for production deployments.

### Creating a YAML Config

**face_config.yaml:**
```yaml
# Model configuration for face detection
face_detector:
  hardware: HAILORT/HAILO8
  inference_host_address: "@local"
  model_zoo_url: degirum/hailo

# Model configuration for face embedding
face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@local"
  model_zoo_url: degirum/hailo

# Database configuration
db_path: ./face_recognition_db.lance
cosine_similarity_threshold: 0.6

# Face filtering (optional)
face_filters:
  enable_small_face_filter: true
  min_face_size: 50
  enable_frontal_filter: true
  enable_shift_filter: true
```

### Loading from YAML

```python
import degirum_face

# Load configuration from file
config, settings = degirum_face.FaceRecognizerConfig.from_yaml(
    yaml_file="face_config.yaml"
)

# Create recognizer
face_recognizer = degirum_face.FaceRecognizer(config)
```

**Returns:**
- `config` - Initialized `FaceRecognizerConfig` object
- `settings` - Raw dictionary (useful for debugging)

### Loading from YAML String

```python
yaml_string = """
face_detector:
  hardware: OPENVINO/CPU
  inference_host_address: "@local"
face_embedder:
  hardware: OPENVINO/CPU
  inference_host_address: "@local"
db_path: ./face_db.lance
cosine_similarity_threshold: 0.6
"""

config, settings = degirum_face.FaceRecognizerConfig.from_yaml(
    yaml_str=yaml_string
)
```

### Benefits of YAML

- **Clean separation** - Config separate from code
- **Easy modification** - Change hardware without editing code
- **Version control** - Track config changes in git
- **Team collaboration** - Share standardized configs
- **Multiple environments** - dev.yaml, staging.yaml, prod.yaml

## Similarity Threshold Tuning

The similarity threshold controls match strictness:

```python
config = degirum_face.FaceRecognizerConfig(
    cosine_similarity_threshold=0.50  # Adjust based on use case
)
```

### Threshold Guide

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 0.30-0.40 | Very lenient | Maximum recall, accept some false positives |
| 0.50-0.60 | Balanced | General use (recommended starting point) |
| 0.65-0.75 | Strict | High precision, minimize false positives |
| 0.80+ | Very strict | Security applications |

### Tuning Strategy

1. **Start with 0.50** - Good balance for most cases
2. **Test with real data** - Process representative images
3. **Adjust based on results:**
   - Too many false positives? Increase threshold
   - Missing valid matches? Decrease threshold
4. **Consider use case:**
   - Access control: Higher threshold (0.65-0.75)
   - Photo organization: Lower threshold (0.45-0.55)

## Database Management

### Database Paths

Use separate databases for different hardware:

```python
# Different databases for different accelerators
config_hailo = degirum_face.FaceRecognizerConfig(
    db_path="./face_db_hailo8.lance",
    # ...
)

config_cpu = degirum_face.FaceRecognizerConfig(
    db_path="./face_db_cpu.lance",
    # ...
)
```

**Why?** Different hardware may produce slightly different embeddings.

### Database Operations

```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# List all enrolled identities
identities = face_recognizer.list_identities()
print(f"Enrolled: {identities}")

# Remove a specific person
face_recognizer.delete_identity("Bob")

# Clear entire database
face_recognizer.clear_database()
```

## Next Steps

- **[Methods Reference](methods.md)** - Complete API documentation
- **[Deployment Guide](deployment.md)** - Hardware selection and production setup
- **[Face Filters Reference](../../reference/face-filters.md)** - Quality filtering options
- **[YAML Configuration Reference](../../reference/yaml-config.md)** - Complete YAML schema
