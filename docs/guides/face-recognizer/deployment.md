# Hardware & Deployment Guide

Complete guide to deploying `FaceRecognizer` on different hardware accelerators and inference environments.

## Deployment Options

Choose where your models run:

| Option | Use Case | Pros | Cons |
|--------|----------|------|------|
| **Cloud (`@cloud`)** | Experimentation, prototyping | No hardware needed, all accelerators available | Internet required, higher latency |
| **Local (`@local`)** | Edge deployment, production | Lowest latency, data privacy, offline | Requires local hardware & drivers |
| **Remote Server** | Centralized inference | Shared resources, scalable | Network dependency, server setup |

## Cloud Inference

Run models on DeGirum AI Hub without any local hardware setup.

### Configuration

```python
import degirum_face

detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"  # DeGirum AI Hub
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,
    face_embedding_model_spec=embedding_spec,
    db_path="./face_db.lance",
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

### When to Use

- **Experimentation** - Try different hardware accelerators
- **Prototyping** - Build and test without hardware procurement
- **Development** - Develop on laptop, deploy to edge later
- **Evaluation** - Compare performance across accelerators

### Limitations

- Requires internet connection
- Higher latency than local inference
- Data leaves your system (sent to cloud for processing)

## Local Inference

Run models directly on your local hardware accelerator.

### Configuration

```python
import degirum_face

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
    db_path="./face_db.lance",
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

### When to Use

- **Production edge deployments**
- **Offline operation** (no internet needed)
- **Low latency requirements**
- **Data privacy** (data stays local)

### Requirements

- Compatible hardware accelerator installed
- Platform-specific drivers (see [Supported Hardware](#supported-hardware))

## Remote AI Server

Connect to a dedicated inference server on your network.

### Configuration

```python
import degirum_face

detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="TENSORRT/GPU",
    inference_host_address="192.168.1.100:8778"  # Server IP:port
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="TENSORRT/GPU",
    inference_host_address="192.168.1.100:8778"
)

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,
    face_embedding_model_spec=embedding_spec,
    db_path="./face_db.lance",
)

face_recognizer = degirum_face.FaceRecognizer(config)
```

### When to Use

- **Centralized GPU/accelerator resources**
- **Multiple client devices** sharing one inference server
- **Private cloud deployments**
- **Cost optimization** - One powerful server vs many edge devices

### Setup

See [AI Server Setup Guide](https://docs.degirum.com/pysdk/user-guide-pysdk/setting-up-an-ai-server) for deployment instructions.

## Supported Hardware

### CPU (No Accelerator)

**Device Type:** `TFLITE/CPU`

**Use Case:** Development, low-volume processing, universal compatibility

```python
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="TFLITE/CPU",
    inference_host_address="@local"
)
```

**Installation:** None required (works everywhere)

### Hailo AI Accelerators

**Device Types:**
- `HAILORT/HAILO8` - Hailo-8 accelerator (26 TOPS)
- `HAILORT/HAILO8L` - Hailo-8L accelerator (13 TOPS)

**Use Case:** Edge AI, embedded systems, robotics

**Installation:** [Hailo Runtime](https://docs.degirum.com/pysdk/user-guide-pysdk/installing-hailort-runtime)

```python
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@local"
)
```

### Intel Platforms

**Device Types:**
- `OPENVINO/CPU` - Intel CPU optimization
- `OPENVINO/GPU` - Intel integrated/discrete GPU
- `OPENVINO/NPU` - Intel Neural Processing Unit (Core Ultra)

**Use Case:** Intel workstations, laptops with Core Ultra

**Installation:** [OpenVINO Runtime](https://docs.degirum.com/pysdk/user-guide-pysdk/installing-openvino-runtime)

```python
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="OPENVINO/NPU",
    inference_host_address="@local"
)
```

### NVIDIA GPUs

**Device Type:** `TENSORRT/GPU`

**Use Case:** High-throughput, server deployments, workstations

**Installation:** [TensorRT Runtime](https://docs.degirum.com/pysdk/user-guide-pysdk/installing-tensorrt-runtime)

```python
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="TENSORRT/GPU",
    inference_host_address="@local"
)
```

### DeGirum ORCA

**Device Type:** `N2X/ORCA1`

**Use Case:** DeGirum's own accelerator platform

**Installation:** [ORCA SDK](https://docs.degirum.com/)

```python
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="N2X/ORCA1",
    inference_host_address="@local"
)
```

### Other Accelerators

**Axelera Metis:**
- Device Type: `AXELERA/METIS`
- [Metis SDK](https://docs.degirum.com/)

**DEEPX M1A:**
- Device Type: `DEEPX/M1A`
- [DEEPX SDK](https://docs.degirum.com/)

**Rockchip RK3588:**
- Device Type: `RKNN/RK3588`
- [RKNN SDK](https://docs.degirum.com/)

**Google Edge TPU:**
- Device Type: `TFLITE/EDGETPU`
- [Edge TPU Runtime](https://coral.ai/docs/accelerator/get-started/)

## Hardware Discovery

### Check Supported Hardware

See what hardware types the model registry supports:

```python
import degirum_face

# What hardware does degirum-face support?
registry_hw = degirum_face.model_registry.get_hardware()
print(f"Supported: {registry_hw}")
# Output: ['HAILORT/HAILO8', 'N2X/ORCA1', 'OPENVINO/CPU', ...]
```

### Check Available Hardware

See what's actually available on your inference host:

```python
# Check cloud availability
available_hw = degirum_face.get_system_hw("@cloud")
print(f"Available on cloud: {available_hw}")

# Check local hardware
local_hw = degirum_face.get_system_hw("@local")
print(f"Available locally: {local_hw}")
```

### Find Compatible Hardware

Get the intersection (supported AND available):

```python
# What can I use right now?
compatible_hw = degirum_face.get_compatible_hw("@cloud")
print(f"Ready to use: {compatible_hw}")
```

## Hardware Selection Strategy

### 1. Start with Cloud

Experiment with different accelerators without hardware setup:

```python
import degirum_face

# Try different hardware types on cloud
hardware_options = ["N2X/ORCA1", "HAILORT/HAILO8", "OPENVINO/NPU", "TENSORRT/GPU"]

for hw_type in hardware_options:
    print(f"\nTesting {hw_type}...")
    
    config = degirum_face.FaceRecognizerConfig(
        face_detection_model_spec=degirum_face.get_face_detection_model_spec(
            device_type=hw_type,
            inference_host_address="@cloud"
        ),
        face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
            device_type=hw_type,
            inference_host_address="@cloud"
        ),
        db_path=f"./face_db_{hw_type.replace('/', '_').lower()}.lance",
    )
    
    recognizer = degirum_face.FaceRecognizer(config)
    
    # Test with your workload
    # Measure: inference speed, accuracy, etc.
```

### 2. Evaluate Performance

Test with your actual workload:
- **Throughput** - Frames per second
- **Latency** - Response time
- **Accuracy** - Recognition quality
- **Power consumption** - For battery/embedded use

### 3. Deploy Locally

Once you've chosen hardware, deploy to production:

```python
# Production configuration
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",  # Your chosen hardware
    inference_host_address="@local"  # Production deployment
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@local"
)

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,
    face_embedding_model_spec=embedding_spec,
    db_path="./face_db_production.lance",
    cosine_similarity_threshold=0.6,
)
```

## Production Deployment Example

### Local Edge Deployment (Hailo-8)

Complete example for edge device:

```python
import degirum_face

# Configuration
DEVICE_TYPE = "HAILORT/HAILO8"
INFERENCE_HOST = "@local"

# Get model specs
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type=DEVICE_TYPE,
    inference_host_address=INFERENCE_HOST,
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type=DEVICE_TYPE,
    inference_host_address=INFERENCE_HOST,
)

# Create configuration
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,
    face_embedding_model_spec=embedding_spec,
    db_path="./face_db_hailo8.lance",
    cosine_similarity_threshold=0.6,
)

# Create recognizer
face_recognizer = degirum_face.FaceRecognizer(config)

# Use in application
face_recognizer.enroll_image('person.jpg', 'John Doe')
result = face_recognizer.predict('test.jpg')
```

### Database per Hardware Type

**Important:** Use separate databases for different hardware types, as embeddings may vary slightly:

```python
# Different databases for different accelerators
config_hailo = degirum_face.FaceRecognizerConfig(
    db_path="./face_db_hailo8.lance",
    # ... Hailo specs
)

config_cpu = degirum_face.FaceRecognizerConfig(
    db_path="./face_db_cpu.lance",
    # ... CPU specs
)
```

## Recommended Workflow

1. **Prototype on cloud** - Experiment with `@cloud` to find best hardware
2. **Test configuration** - Validate models and thresholds
3. **Deploy to edge** - Switch to `@local` for production
4. **Monitor performance** - Track inference speed and accuracy

## Next Steps

- **[Configuration Guide](configuration.md)** - Customize your deployment
- **[Methods Reference](methods.md)** - Complete API documentation  
- **[Face Filters](../../reference/face-filters.md)** - Quality filtering options
