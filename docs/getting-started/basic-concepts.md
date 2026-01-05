# Basic Concepts

## What Can You Do With degirum-face?

`degirum-face` enables face recognition workflows across images and video:

- **Detect and identify** faces in photos, video files, and live streams
- **Enroll faces** into a database with custom attributes (names, metadata)
- **Track faces** across video frames with persistent IDs
- **Real-time alerts** when specific people are detected
- **Batch processing** for large image collections
- **Automated clip extraction** for detected faces

All with minimal code and flexible deployment options.

## Deployment Options

### Where Can It Run?

The `inference_host_address` parameter controls where your models execute:

| Option | Description | Best For |
|--------|-------------|----------|
| **Cloud (`@cloud`)** | Models run on DeGirum's cloud servers | Quick start, experimentation, trying different hardware |
| **Local (`@local`)** | Models run on your machine | Production, lowest latency, full privacy, offline operation |
| **AI Server** | Models run on a dedicated server (e.g., `server-ip:port`) | Centralized GPU/accelerator resources on your network |

**Cloud** is ideal for getting started quickly without hardware setup. **Local** gives you complete control and privacy. **AI Server** lets you share powerful hardware across multiple applications. See [AI Server Setup Guide](https://docs.degirum.com/pysdk/user-guide-pysdk/setting-up-an-ai-server) for server deployment.

### What Hardware Is Supported?

The `device_type` parameter specifies which accelerator to use. Works on CPU, GPU, and a wide range of edge AI accelerators:

- **Hailo** (HAILORT/HAILO8, HAILORT/HAILO8L)
- **Axelera** (AXELERA/METIS)
- **DEEPX** (DEEPX/M1A)
- **Intel** (OPENVINO/CPU, OPENVINO/GPU, OPENVINO/NPU)
- **NVIDIA** (TENSORRT/GPU)
- **Rockchip** (RKNN/RK3588)
- **Google** (TFLITE/EDGETPU)
- **DeGirum** (N2X/ORCA1)

See [DeGirum PySDK Installation](https://docs.degirum.com/pysdk/installation) for platform requirements and [Runtimes & Drivers](https://docs.degirum.com/pysdk/runtimes-and-drivers) for hardware-specific setup.

### Discovering Available Hardware

Use helper functions to check what's supported and available before configuring:

```python
# See all supported hardware platforms
supported = degirum_face.model_registry.get_hardware()

# Check what's available on cloud or local
available = degirum_face.get_system_hw("@cloud")

# Find compatible hardware you can use right now
compatible = degirum_face.get_compatible_hw("@cloud")
```

## Model Registry

`degirum-face` includes a curated **model registry** - a collection of pre-optimized face detection and embedding models for various hardware platforms. The registry automatically selects the best model for your chosen hardware, eliminating the need to manually pick models or tune parameters.

Helper functions like `get_face_detection_model_spec()` and `get_face_embedding_model_spec()` query this registry to get optimized models for your hardware. For complete control, you can also provide custom models outside the registry.

## Core Components

`degirum-face` provides four main components:

**FaceRecognizer** - For static images and batch processing
- Process photos or image collections
- Enroll faces into the database
- One-time batch recognition

**FaceTracker** - For video streams and real-time monitoring
- Monitor live camera feeds or video files
- Track faces across frames with persistent IDs
- Generate real-time alerts and automated clip extraction

**FaceClipManager** - For managing saved video clips
- List and retrieve video clips from object storage (S3 or local)
- Access clips recorded by FaceTracker alerts
- Download and manage alert recordings

**Database** - For managing the face recognition database
- Query and search enrolled faces
- Add, update, or delete face records
- Direct access to LanceDB storage for advanced operations

---

Before diving into the component-specific guides, let's understand the underlying recognition pipeline that powers all these tools.

## The Recognition Pipeline

Both FaceRecognizer and FaceTracker use the same core pipeline for processing faces:

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│ Input Image │ ──> │ Face Detection + │ ──> │   Align &    │ ──> │   Embedding  │
│             │     │    Landmarks     │     │   Extract    │     │  Extraction  │
└─────────────┘     └──────────────────┘     └──────────────┘     └──────────────┘
                                                                            │
                                                                            v
                                                                    ┌──────────────┐
                                                                    │   Database   │
                                                                    │   Search &   │
                                                                    │    Match     │
                                                                    └──────────────┘
```

### 1. Face Detection + Landmarks
Locates faces in the image and detects 5 facial keypoints (eyes, nose, mouth corners) in a single pass.

**Output:** Bounding box coordinates + 5 landmark points per face

### 2. Alignment & Extraction
Aligns each detected face to a standard pose using the landmarks, then extracts a normalized face crop.

**Output:** Aligned face image (typically 112×112 pixels)

### 3. Embedding Extraction
Converts the aligned face into a numerical vector (embedding) that captures unique facial features.

**Output:** Embedding vector (typically 512 dimensions)

### 4. Database Search & Matching
Compares the embedding against enrolled faces using cosine similarity.

**Database:** LanceDB (vector database)  
**Output:** Identity + similarity score

### Additional Capabilities

**Face Quality Filters** (optional) - Applied after detection to ensure only high-quality faces are processed. Filters include minimum size, pose angle, blur detection, brightness checks, and more. See [Face Filters Reference](../reference/face-filters.md).

**Tracking** (FaceTracker only) - Maintains persistent IDs for faces across video frames using visual tracking and re-identification. Enables features like trajectory tracking, adaptive embedding extraction, and temporal consistency.

**Alert & Recording** (FaceTracker only) - Triggers events when known/unknown faces are detected and automatically records video clips to object storage (S3 or local filesystem).

## Understanding Results

Results are returned as `FaceRecognitionResult` objects containing detected faces with their identities and metadata:

```python
result = face_recognizer.predict("photo.jpg")

for face in result.faces:
    if face.attributes:
        print(f"Known: {face.attributes} (confidence: {face.similarity_score:.2f})")
    else:
        print("Unknown person")
```

**Key properties:**
- `attributes` - Person's name (or `None` if unknown)
- `similarity_score` - Match confidence (0.0-1.0)
- `bbox` - Face bounding box
- `images` - Cropped face images (numpy arrays)

See [FaceRecognitionResult Reference](../reference/face-recognition-result.md) for complete property list and usage examples.

---

## Next Steps

Now that you understand deployment options, hardware support, the core components, and how the recognition pipeline works, you're ready to start using degirum-face.

**Choose your path:**
- **Process images or batches** → [FaceRecognizer Guide](../guides/face-recognizer/overview.md)
- **Monitor video streams** → [FaceTracker Guide](../guides/face-tracker/overview.md)
- **Manage video clips** → [FaceClipManager Guide](../guides/face-clip-manager/overview.md)
- **Query the database** → [Database Guide](../guides/database/overview.md)

