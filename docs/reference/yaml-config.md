# YAML Configuration Reference

Complete schema and examples for configuring `degirum-face` with YAML files.

## Overview

YAML configuration files provide a clean way to configure `FaceRecognizer` and `FaceTracker` without embedding configuration in code.

### Benefits

- **Separation of concerns** - Config separate from application logic
- **Easy modification** - Change settings without code changes
- **Version control** - Track configuration changes in git
- **Multiple environments** - dev.yaml, staging.yaml, prod.yaml
- **Team collaboration** - Standardized configurations

## FaceRecognizer YAML Schema

### Complete Example

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
  enable_zone_filter: false
```

### Field Reference

#### face_detector (required)

Configuration for face detection model.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `hardware` | string | Hardware accelerator type | `"HAILORT/HAILO8"` |
| `inference_host_address` | string | Where to run inference | `"@local"`, `"@cloud"`, `"192.168.1.100:8778"` |
| `model_zoo_url` | string | Model zoo URL (optional) | `"degirum/hailo"` |

**Hardware options:**
- `TFLITE/CPU` - CPU only
- `HAILORT/HAILO8`, `HAILORT/HAILO8L` - Hailo accelerators
- `OPENVINO/CPU`, `OPENVINO/GPU`, `OPENVINO/NPU` - Intel platforms
- `TENSORRT/GPU` - NVIDIA GPU
- `N2X/ORCA1` - DeGirum ORCA
- `AXELERA/METIS`, `DEEPX/M1A`, `RKNN/RK3588`, `TFLITE/EDGETPU` - Other accelerators

#### face_embedder (required)

Configuration for face embedding model. Same fields as `face_detector`.

```yaml
face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@local"
```

#### db_path (required)

Path to LanceDB database file for storing face embeddings.

```yaml
db_path: ./face_recognition_db.lance
```

#### cosine_similarity_threshold (required)

Minimum similarity score (0.0-1.0) to consider faces a match.

```yaml
cosine_similarity_threshold: 0.6  # 0.3-0.8 typical range
```

#### face_filters (optional)

Face quality filtering configuration. See [Face Filters Reference](face-filters.md).

```yaml
face_filters:
  # Small face filter
  enable_small_face_filter: true
  min_face_size: 50
  
  # Zone filter
  enable_zone_filter: true
  zone:
    - [100, 100]
    - [500, 100]
    - [500, 400]
    - [100, 400]
  
  # Geometric filters
  enable_frontal_filter: true
  enable_shift_filter: true
```

---

## FaceTracker YAML Schema

### Complete Example

```yaml
# Video source configuration
video_source: "rtsp://192.168.1.100/stream"

# Face detection model
face_detection_model_zoo_url: degirum/public
face_detection_model_name: yolov8n_relu6_face_det--512x512_quant_n2x_orca1_1
inference_host_address: "@local"

# Landmark model
landmark_model_zoo_url: degirum/public
landmark_model_name: mobilefacenet_lmks_5pt--112x112_quant_n2x_orca1_1

# Embedding model
embedding_model_zoo_url: degirum/public
embedding_model_name: arcface_resnet100--112x112_quant_n2x_orca1_1

# Database
face_database_path: "./face_database.lance"
similarity_threshold: 0.50

# Confirmation configuration
confirmation_type: "consecutive"
confirmation_frames: 3

# Alerting configuration
alerting_enabled: true
alerting_mode: "all"

# Clip storage configuration
clip_storage_enabled: true
clip_storage_output_folder: "./face_clips"
clip_storage_duration_seconds: 5
clip_storage_include_thumbnail: true

# Streaming configuration
streaming_enabled: false

# ReID filter
reid_expiration_frames: 30
```

### Field Reference

#### Video Source

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `video_source` | string | Video input source | `"rtsp://..."`, `"0"` (webcam), `"video.mp4"` |

#### Model Configuration

| Field | Type | Description |
|-------|------|-------------|
| `face_detection_model_zoo_url` | string | Detection model zoo URL |
| `face_detection_model_name` | string | Detection model name |
| `landmark_model_zoo_url` | string | Landmark model zoo URL |
| `landmark_model_name` | string | Landmark model name |
| `embedding_model_zoo_url` | string | Embedding model zoo URL |
| `embedding_model_name` | string | Embedding model name |
| `inference_host_address` | string | Inference location |

#### Database

| Field | Type | Description |
|-------|------|-------------|
| `face_database_path` | string | Path to LanceDB file |
| `similarity_threshold` | float | Match threshold (0.0-1.0) |

#### Confirmation

| Field | Type | Description | Options |
|-------|------|-------------|---------|
| `confirmation_type` | string | Confirmation logic | `"consecutive"`, `"cumulative"` |
| `confirmation_frames` | int | Frames required | Typically 3-5 |

#### Alerting

| Field | Type | Description | Options |
|-------|------|-------------|---------|
| `alerting_enabled` | bool | Enable alerts | `true`, `false` |
| `alerting_mode` | string | When to alert | `"all"`, `"known"`, `"unknown"` |

#### Clip Storage

| Field | Type | Description |
|-------|------|-------------|
| `clip_storage_enabled` | bool | Enable clip saving |
| `clip_storage_output_folder` | string | Where to save clips |
| `clip_storage_duration_seconds` | int | Clip length |
| `clip_storage_include_thumbnail` | bool | Save face thumbnail |

#### Streaming

| Field | Type | Description |
|-------|------|-------------|
| `streaming_enabled` | bool | Enable MJPEG streaming |
| `streaming_port` | int | Server port (optional) |

#### ReID Filter

| Field | Type | Description |
|-------|------|-------------|
| `reid_expiration_frames` | int | Frames before re-embedding |

---

## Loading YAML Configurations

### FaceRecognizer

```python
import degirum_face

# Load from file
config, settings = degirum_face.FaceRecognizerConfig.from_yaml(
    yaml_file="face_config.yaml"
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

### FaceTracker

```python
import degirum_face

# Load from file
config = degirum_face.FaceTrackerConfig.from_yaml("tracker_config.yaml")

face_tracker = degirum_face.FaceTracker(config)
```

### Loading from String

```python
yaml_string = """
face_detector:
  hardware: TFLITE/CPU
  inference_host_address: "@local"
face_embedder:
  hardware: TFLITE/CPU
  inference_host_address: "@local"
db_path: ./face_db.lance
cosine_similarity_threshold: 0.6
"""

config, settings = degirum_face.FaceRecognizerConfig.from_yaml(
    yaml_str=yaml_string
)
```

---

## Configuration Templates

### CPU Development (No Accelerator)

```yaml
face_detector:
  hardware: TFLITE/CPU
  inference_host_address: "@local"

face_embedder:
  hardware: TFLITE/CPU
  inference_host_address: "@local"

db_path: ./face_db_dev.lance
cosine_similarity_threshold: 0.6
```

### Cloud Experimentation

```yaml
face_detector:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"

face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"

db_path: ./face_db_cloud.lance
cosine_similarity_threshold: 0.6
```

### Edge Production (Hailo-8)

```yaml
face_detector:
  hardware: HAILORT/HAILO8
  inference_host_address: "@local"
  model_zoo_url: degirum/hailo

face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@local"
  model_zoo_url: degirum/hailo

db_path: ./face_db_production.lance
cosine_similarity_threshold: 0.6

face_filters:
  enable_frontal_filter: true
  enable_small_face_filter: true
  min_face_size: 60
  enable_shift_filter: true
```

### Intel NPU Deployment

```yaml
face_detector:
  hardware: OPENVINO/NPU
  inference_host_address: "@local"

face_embedder:
  hardware: OPENVINO/NPU
  inference_host_address: "@local"

db_path: ./face_db_intel.lance
cosine_similarity_threshold: 0.6
```

### NVIDIA GPU Server

```yaml
face_detector:
  hardware: TENSORRT/GPU
  inference_host_address: "192.168.1.100:8778"

face_embedder:
  hardware: TENSORRT/GPU
  inference_host_address: "192.168.1.100:8778"

db_path: ./face_db_tensorrt.lance
cosine_similarity_threshold: 0.6
```

---

## Best Practices

### Environment-Specific Configs

Maintain separate configurations for each environment:

```
configs/
  ├── dev.yaml          # Development (CPU)
  ├── staging.yaml      # Staging (cloud)
  └── production.yaml   # Production (local hardware)
```

**Usage:**
```python
import os
import degirum_face

env = os.getenv("ENV", "dev")
config_file = f"configs/{env}.yaml"

config, _ = degirum_face.FaceRecognizerConfig.from_yaml(yaml_file=config_file)
face_recognizer = degirum_face.FaceRecognizer(config)
```

### Version Control

Commit YAML files to version control:

```gitignore
# .gitignore
*.lance          # Don't commit databases
face_clips/      # Don't commit video clips

# DO commit config files
!configs/*.yaml
```

### Documentation

Add comments to YAML files:

```yaml
# Production configuration for Hailo-8 edge deployment
# Last updated: 2025-01-02
# Contact: ops@example.com

face_detector:
  hardware: HAILORT/HAILO8  # 26 TOPS accelerator
  inference_host_address: "@local"

# Threshold tuned for our use case (access control)
cosine_similarity_threshold: 0.65  # Stricter for security
```

---

## Validation

Check configuration before deployment:

```python
import degirum_face

try:
    config, settings = degirum_face.FaceRecognizerConfig.from_yaml(
        yaml_file="production.yaml"
    )
    print("Configuration valid!")
    print(f"Hardware: {settings['face_detector']['hardware']}")
    print(f"Inference: {settings['face_detector']['inference_host_address']}")
except Exception as e:
    print(f"Configuration error: {e}")
```

## Next Steps

- **[Configuration Guide](../guides/face-recognizer/configuration.md)** - Configuration concepts
- **[Face Filters Reference](face-filters.md)** - Filter options
- **[Deployment Guide](../guides/face-recognizer/deployment.md)** - Production deployment
