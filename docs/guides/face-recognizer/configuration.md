# FaceRecognizer Configuration

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

A `ModelSpec` tells `degirum-face` which model to load and where to run it. You have two options:

### Option 1: Use the Model Registry (Recommended)

The `degirum-face` model registry provides pre-optimized models for all supported hardware. Use helper functions to automatically select the best model:

```python
import degirum_face

# Get detection model
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)

# Get embedding model
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
```

**Parameters:**
- `device_type` - Hardware accelerator (see [Basic Concepts](../../getting-started/basic-concepts.md#what-hardware-is-supported) for all options)
- `inference_host_address` - Inference location: `@cloud`, `@local`, or AI server address (see [Basic Concepts](../../getting-started/basic-concepts.md#where-can-it-run))

### Option 2: Bring Your Own Models

For complete customization (using models outside the registry), create custom `ModelSpec` objects directly. See [ModelSpec Documentation](https://docs.degirum.com/degirum-tools/model_registry#modelspec) for details.

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

## Database Path

Enrolled face embeddings are stored in a LanceDB database file specified by `db_path`:

```python
config = degirum_face.FaceRecognizerConfig(
    db_path="./face_db.lance",  # LanceDB file path
    # ...
)
```

**Important:** `degirum-face` enforces that a database created with one hardware type cannot be used with a different hardware type, as embeddings may vary between accelerators. The system will throw an error if you attempt to mix hardware types with the same database.

## YAML Configuration

`FaceRecognizerConfig` can be initialized from a YAML file or string using the `from_yaml()` method. This approach separates configuration from code, making it easier to version control settings, share configurations across teams, and maintain different configs for development, staging, and production environments.

### Creating a YAML Config

**face_config.yaml:**
```yaml
# Model configuration for face detection
face_detector:
  hardware: HAILORT/HAILO8
  inference_host_address: "@local"
  
# Model configuration for face embedding
face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@local"
  
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