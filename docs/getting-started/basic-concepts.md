# Basic Concepts

Core concepts to understand when working with `degirum-face`.

## Face Recognition vs. Face Tracking

`degirum-face` provides two main approaches:

| | **FaceRecognizer** | **FaceTracker** |
|---|---|---|
| **Use Case** | Static images or batches | Video streams or files |
| **Temporal Awareness** | None (each image is independent) | Tracks faces across frames |
| **Real-Time Events** | No | Yes (alerts, streaming) |
| **Primary Methods** | `predict()`, `predict_batch()`, `enroll_image()` | `start_face_tracking_pipeline()`, `find_faces_in_file()` |
| **Best For** | Photo albums, batch processing | Surveillance, video analysis |

**When to use FaceRecognizer:**
- Processing photos or image collections
- One-time batch recognition
- Building a face database from images

**When to use FaceTracker:**
- Live camera feeds or video files
- Tracking the same person across frames
- Real-time alerts and clip extraction

## Face Recognition Pipeline

Every face recognition operation goes through these stages:

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

## Model Registry

`degirum-face` includes a curated **model registry** - a collection of pre-optimized face detection and embedding models for various hardware platforms. The registry automatically selects the best model for your chosen hardware, so you don't need to manually pick models or tune parameters.

Helper functions like `get_face_detection_model_spec()` and `get_face_embedding_model_spec()` query this registry to get optimized models for your hardware. For complete control, you can also provide custom models outside the registry.

## Face Recognition Results

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

## Deployment & Hardware

### Inference Location (inference_host_address)

The `inference_host_address` parameter controls where your models run:

| Option | Use Case | Best For |
|--------|----------|----------|
| **Cloud (`@cloud`)** | Experimentation | Try any hardware without local setup |
| **Local (`@local`)** | Production | Lowest latency, full privacy, offline |
| **AI Server** | Centralized | Shared GPU/accelerator resources on your network |


**Cloud** runs models on DeGirum's servers, **Local** runs on your machine, and **AI Server** runs on a dedicated inference server you set up. See [AI Server Setup Guide](https://docs.degirum.com/pysdk/user-guide-pysdk/setting-up-an-ai-server) for server deployment.

### Hardware Accelerators (device_type)

Works on CPU, GPU, and a wide range of edge AI accelerators. The `device_type` parameter specifies which hardware to use:

- **Hailo** (HAILORT/HAILO8, HAILORT/HAILO8L)
- **Axelera** (AXELERA/METIS)
- **DEEPX** (DEEPX/M1A)
- **Intel** (OPENVINO/CPU, OPENVINO/GPU, OPENVINO/NPU)
- **NVIDIA** (TENSORRT/GPU)
- **Rockchip** (RKNN/RK3588)
- **Google** (TFLITE/EDGETPU)
- **DeGirum** (N2X/ORCA1)

See [DeGirum PySDK Installation](https://docs.degirum.com/pysdk/installation) for requirements and [Runtimes & Drivers](https://docs.degirum.com/pysdk/runtimes-and-drivers) for hardware setup.

### Discovery

`degirum-face` provides helper functions to discover what hardware is supported and available. Use these to check compatibility before configuring your models.

```python
# See what's supported
supported = degirum_face.model_registry.get_hardware()

# See what's available on cloud/local
available = degirum_face.get_system_hw("@cloud")

# Find what you can use right now
compatible = degirum_face.get_compatible_hw("@cloud")
```

