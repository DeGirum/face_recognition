# Advanced Usage Guide for degirum-face

This guide covers advanced topics for production deployments, hardware optimization, and custom configurations.

## Prerequisites

Before reading this guide, you should:
- Have completed the [Quickstart](README.md#quickstart) and successfully run basic face recognition
- Understand the basics: `FaceRecognizer`, `enroll_image()`, and `predict()`
- Know what the quickstart default configuration uses (TFLITE/CPU running locally)

## Table of Contents
- [Understanding the Quickstart Defaults](#understanding-the-quickstart-defaults)
- [Anatomy of FaceRecognizerConfig](#anatomy-of-facerecognizerconfig)
- [FaceRecognizer Methods](#facerecognizer-methods)
- [Where Inference Runs: Deployment Options](#where-inference-runs-deployment-options)
- [Choosing Hardware: Discovery and Selection](#choosing-hardware-discovery-and-selection)
- [Configuring for Specific Hardware](#configuring-for-specific-hardware)
- [Using YAML Configuration Files](#using-yaml-configuration-files)
- [Face Filtering Configuration](#face-filtering-configuration)

---

## Understanding the Quickstart Defaults

The quickstart example uses this simple code:

```python
face_recognizer = degirum_face.FaceRecognizer()
```

**What's happening here?** `FaceRecognizer` requires a `FaceRecognizerConfig` object. When you don't provide one, it creates a **default configuration** automatically. This is equivalent to:

```python
# What the quickstart actually does behind the scenes
default_config = degirum_face.FaceRecognizerConfig()  # Uses all defaults
face_recognizer = degirum_face.FaceRecognizer(default_config)
```

The default configuration uses these settings:
- **Hardware:** `TFLITE/CPU` (works on any machine, no special hardware needed)
- **Inference location:** `@local` (runs on your local machine)
- **Database:** `./face_reid_db.lance` (local file)
- **Similarity threshold:** `0.6` (balanced accuracy)

**Why customize?** For production deployments, you may want to:
- Use **hardware accelerators** (Hailo, NVIDIA GPU, Intel NPU) for better performance
- Run inference in the **cloud** to experiment with different hardware without local setup
- Deploy to **edge devices** for offline, low-latency operation
- Tune **thresholds and filters** for your specific use case

The rest of this guide shows you how to create custom `FaceRecognizerConfig` objects and pass them to `FaceRecognizer`.

---

## Anatomy of FaceRecognizerConfig

`FaceRecognizer` is configured entirely through a `FaceRecognizerConfig` object. Understanding its structure is key to customization.

Every `FaceRecognizerConfig` contains these components:

### 1. Face Detection Model Spec (Required)
Specifies which model to use for **detecting faces** in images. This model finds faces and their bounding boxes.

### 2. Face Embedding Model Spec (Required)
Specifies which model to use for **extracting face embeddings** (numerical representations) for recognition. These embeddings are used for matching faces.

### 3. Database Path (Required)
Where to store the face embeddings database (`.lance` file). This is your "face gallery" for recognition.

### 4. Similarity Threshold (Required)
The minimum cosine similarity score (0.0-1.0) to consider two faces a match. Higher = stricter matching.

### 5. Face Filters (Optional)
Optional filtering rules to improve recognition quality by skipping low-quality detections. Controlled by a `FaceFilterConfig` object. Common filters include small face filter, frontal filter, shift filter, and zone filter.

See [Face Filtering Configuration](#face-filtering-configuration) for configuration details and examples.

### What is a Model Spec?

A `ModelSpec` tells `degirum-face` **which model** to load and **where to run it**. It's part of the `degirum_tools` package and is documented in detail at [degirum-tools ModelSpec documentation](https://docs.degirum.com/degirum-tools/model_registry#modelspec).

For face recognition, each model spec requires:
- **`device_type`** - The hardware to use (e.g., `"HAILORT/HAILO8"`, `"OPENVINO/CPU"`, `"N2X/ORCA1"`)
- **`inference_host_address`** - Where to run inference (`"@cloud"`, `"@local"`, or `"<host>:<port>"`)

### Helper Functions for Model Specs

The `degirum-face` package comes with a **built-in model registry** containing pre-configured face detection and embedding models optimized for various hardware platforms. Instead of manually creating `ModelSpec` objects, use these helper functions that automatically select models from the registry:

```python
import degirum_face

# Get a face detection model spec for specific hardware
face_detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)

# Get a face embedding model spec for the same hardware
face_embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)
```

These helper functions pick the best available models from the `degirum-face` model registry for your specified hardware.

**Advanced:** You can also create custom `ModelSpec` objects to use your own models, but this is not covered in this guide. See the [ModelSpec documentation](https://docs.degirum.com/degirum-tools/model_registry#modelspec) for advanced usage.

### Putting It All Together

Here's how the four components come together in a configuration:

```python
import degirum_face

# 1 & 2: Get model specs for your target hardware
detector_spec = degirum_face.get_face_detection_model_spec(
    device_type="HAILORT/HAILO8",      # Which hardware
    inference_host_address="@cloud"     # Where to run
)
embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type="HAILORT/HAILO8",
    inference_host_address="@cloud"
)

# Create config with all four components
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=detector_spec,     # 1. Detection model
    face_embedding_model_spec=embedding_spec,    # 2. Embedding model
    db_path="./face_db_hailo8.lance",           # 3. Database path
    cosine_similarity_threshold=0.6,             # 4. Matching threshold
    # face_filters=...                           # 5. Optional filters (see Performance Tuning)
)

# Pass the config to FaceRecognizer
face_recognizer = degirum_face.FaceRecognizer(config)

# Now use the recognizer as usual
face_recognizer.enroll_image('person.jpg', 'John Doe')
result = face_recognizer.predict('test.jpg')

# Access recognized faces in the result
for face in result.faces:
    # Each face is a FaceRecognitionResult object with:
    # - attributes: Person name (e.g., "John Doe") or None for unknown
    # - db_id: Database ID if matched
    # - similarity_score: Match confidence (0.0-1.0)
    # - bbox: Bounding box coordinates
    # - detection_score: Face detection confidence
    # - landmarks: Facial keypoints
    # - embeddings: Face embedding vector(s)
    print(face)  # Pretty-printed summary
```

**Key insight:** 
- `FaceRecognizer` always uses a `FaceRecognizerConfig` - either one you provide or the default
- The `device_type` and `inference_host_address` in your model specs determine **what hardware** is used and **where it runs**
- Once configured, the recognizer's API (`enroll_image()`, `predict()`, etc.) stays the same regardless of hardware

The next sections explain the `inference_host_address` and `device_type` options in detail.

---

## FaceRecognizer Methods

Once you've created a configured `FaceRecognizer`, you'll use its methods to enroll known faces and recognize unknown faces. This section covers the four core methods.

### Overview of Methods

| Method | Purpose | Input | Use Case |
|--------|---------|-------|----------|
| `enroll_image()` | Add a single known face to database | One image, one person name | Interactive enrollment, single person registration |
| `enroll_batch()` | Add multiple known faces to database | Multiple images, multiple names | Bulk enrollment, initial database population |
| `predict()` | Recognize faces in a single image | One image | Single photo processing, simple use cases |
| `predict_batch()` | Recognize faces in multiple images | Image iterator (list, video frames, etc.) | Video processing, high-throughput scenarios |

**Key insight:** Use `_batch()` methods whenever processing multiple items for better performance through pipeline parallelism.

---

### enroll_image() - Enroll a Single Face

Enrolls one person's face into the database from a single image.

**Signature:**
```python
enroll_image(frame: Any, attributes: Any) -> np.ndarray
```

**Parameters:**
- `frame` - Image as numpy array or file path (str)
- `attributes` - Person identifier (typically a name string)

**Returns:**
- `np.ndarray` - The face embedding vector that was stored

**Example:**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll from file path
embedding = face_recognizer.enroll_image('photos/alice.jpg', 'Alice')
print(f"Enrolled Alice with embedding shape: {embedding.shape}")

# Enroll from numpy array
import cv2
image = cv2.imread('photos/bob.jpg')
embedding = face_recognizer.enroll_image(image, 'Bob')
```

**How it works:**
1. Detects faces in the image
2. If multiple faces found, selects the largest (by bounding box area)
3. Extracts face embedding
4. Stores embedding in database with the provided attributes

**Best practices:**
- Use clear, frontal face images for enrollment
- One person per enrollment image for best results
- Use consistent naming convention for attributes

---

### enroll_batch() - Enroll Multiple Faces

Enrolls multiple faces from multiple images efficiently.

**Signature:**
```python
enroll_batch(frames: Iterable, attributes: Iterable) -> List[np.ndarray]
```

**Parameters:**
- `frames` - Iterable of images (file paths or numpy arrays)
- `attributes` - Iterable of person identifiers (must match frames order)

**Returns:**
- `List[np.ndarray]` - List of face embeddings that were stored

**Example - Multiple People:**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll multiple people
image_paths = ['alice1.jpg', 'bob1.jpg', 'charlie1.jpg']
names = ['Alice', 'Bob', 'Charlie']

embeddings = face_recognizer.enroll_batch(
    frames=iter(image_paths),
    attributes=iter(names)
)

print(f"Enrolled {len(embeddings)} people")
```

**Example - Multiple Photos of Same Person:**
```python
# Enroll multiple photos of the same person for better accuracy
alice_photos = ['alice1.jpg', 'alice2.jpg', 'alice3.jpg']
alice_names = ['Alice', 'Alice', 'Alice']  # Same name repeated

embeddings = face_recognizer.enroll_batch(
    frames=iter(alice_photos),
    attributes=iter(alice_names)
)

print(f"Enrolled {len(embeddings)} embeddings for Alice")
```

**How it works:**
1. Processes all images through detection → embedding pipeline
2. For each image, selects largest face
3. Stores each embedding with corresponding attributes
4. Pipeline parallelism makes this faster than calling `enroll_image()` repeatedly

**Best practices:**
- Always use iterators: `iter(list)` not just `list`
- Ensure `frames` and `attributes` have same length
- For better accuracy, enroll multiple photos per person from different angles

---

### predict() - Recognize Faces in Single Image

Recognizes all faces in a single image.

**Signature:**
```python
predict(frame: Any) -> InferenceResults
```

**Parameters:**
- `frame` - Image as numpy array or file path (str)

**Returns:**
- `InferenceResults` - Object containing detection results with `.faces` property

**Example:**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll some people first
face_recognizer.enroll_image('alice.jpg', 'Alice')
face_recognizer.enroll_image('bob.jpg', 'Bob')

# Recognize faces in a new image
result = face_recognizer.predict('group_photo.jpg')

# Access recognized faces
print(f"Found {len(result.faces)} faces")

for face in result.faces:
    print(f"Person: {face.attributes}")
    print(f"  Match confidence: {face.similarity_score:.2f}")
    print(f"  Detection confidence: {face.detection_score:.2f}")
    print(f"  Bounding box: {face.bbox}")
    print(f"  Database ID: {face.db_id}")
```

**Understanding the Result:**

The returned object has a `.faces` property containing a list of `FaceRecognitionResult` objects. Each face has:

- **`attributes`** - Matched person name (e.g., "Alice") or `None` if unknown
- **`similarity_score`** - Match confidence 0.0-1.0 (None if unknown)
- **`db_id`** - Database ID if matched
- **`bbox`** - Bounding box coordinates `[x1, y1, x2, y2]`
- **`detection_score`** - Face detection confidence 0.0-1.0
- **`landmarks`** - Facial keypoints (eyes, nose, mouth)
- **`embeddings`** - Face embedding vector(s)

**Example - Pretty Print:**
```python
result = face_recognizer.predict('test.jpg')

for face in result.faces:
    print(face)  # Uses FaceRecognitionResult.__str__() for formatted output
    print()      # Blank line between faces
```

**Example Output:**
```
Attributes      : Alice
Database ID     : 2a3f7c9e
Detection Score : 0.987
Similarity Score: 0.823
Bounding box    : [245, 120, 389, 298]
Landmarks       : 5 points
Embeddings      : 1 vector(s)

Attributes      : None
Database ID     : None
Detection Score : 0.952
Similarity Score: None
Bounding box    : [512, 95, 645, 267]
Landmarks       : 5 points
Embeddings      : 1 vector(s)
```

**When to use:**
- Processing individual photos
- Simple recognition tasks
- Testing and debugging

---

### predict_batch() - Recognize Faces in Multiple Images or Video Streams

Recognizes faces across multiple images or video streams efficiently using pipeline parallelism.

**Signature:**
```python
predict_batch(frames: Iterable) -> Iterator[InferenceResults]
```

**Parameters:**
- `frames` - Iterable of images (file paths, numpy arrays) or video frames from a generator

**Returns:**
- `Iterator[InferenceResults]` - Iterator yielding results for each input frame

**Example 1: Multiple Image Files**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll known faces
face_recognizer.enroll_image('alice.jpg', 'Alice')
face_recognizer.enroll_image('bob.jpg', 'Bob')

# Recognize faces in multiple images
image_paths = ['photo1.jpg', 'photo2.jpg', 'photo3.jpg']

for i, result in enumerate(face_recognizer.predict_batch(iter(image_paths))):
    print(f"\nImage {i+1}: Found {len(result.faces)} faces")
    for face in result.faces:
        if face.attributes:
            print(f"  - {face.attributes} (confidence: {face.similarity_score:.2f})")
        else:
            print(f"  - Unknown person")
```

**Example 2: Video Streams (Recommended)**

For video files, webcams, or RTSP streams, use `degirum_tools` video helpers that handle all video sources:

```python
import degirum_face
from degirum_tools import open_video_stream, video_source, Display

face_recognizer = degirum_face.FaceRecognizer()

# Enroll known faces
face_recognizer.enroll_image('alice.jpg', 'Alice')
face_recognizer.enroll_image('bob.jpg', 'Bob')

# Process video stream (works with webcam, video file, or RTSP)
# Examples: 0 (webcam), 'video.mp4' (file), 'rtsp://camera-ip/stream' (RTSP)
with Display("Face Recognition") as display, open_video_stream(0) as stream:
    for result in face_recognizer.predict_batch(video_source(stream, fps=5)):
        display.show(result)
        
        # Access recognized faces
        for face in result.faces:
            if face.attributes:
                print(f"Recognized: {face.attributes} ({face.similarity_score:.2f})")
```

**What `video_source()` supports:**
- **Webcam:** `open_video_stream(0)` - Index 0, 1, 2, etc.
- **Video file:** `open_video_stream('video.mp4')` - MP4, AVI, etc.
- **RTSP stream:** `open_video_stream('rtsp://192.168.1.100/stream')`
- **FPS control:** `video_source(stream, fps=5)` - Process N frames per second

**Example 3: Custom Generator**

You can also define your own frame generator for custom video sources:

```python
import cv2
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

def custom_frame_generator():
    """Custom generator - process only specific frames, apply preprocessing, etc."""
    cap = cv2.VideoCapture('video.mp4')
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 10th frame
        if frame_count % 10 == 0:
            # Optional: resize, crop, or preprocess
            yield frame
        
        frame_count += 1
    
    cap.release()

# Process with custom generator
for result in face_recognizer.predict_batch(custom_frame_generator()):
    print(f"Faces: {len(result.faces)}")
```

**How it works:**
1. Accepts an iterator/generator yielding frames
2. Processes frames through detection → embedding → matching pipeline
3. Yields results as they're ready (streaming)
4. Pipeline parallelism provides better throughput than calling `predict()` repeatedly

**Performance benefits:**
- **~2-3x faster** than calling `predict()` in a loop
- Pipeline stages (detection, embedding, matching) run in parallel
- Ideal for video streams and high-throughput batch processing

**Best practices:**
- **For video:** Use `degirum_tools.video_source()` - handles webcam, files, RTSP automatically
- **For images:** Use `iter(image_list)` to convert list to iterator
- **Custom needs:** Define your own generator for preprocessing or frame skipping
- **FPS control:** Use `fps=N` parameter to control processing rate (e.g., `fps=5` for 5 frames/sec)
- **Tracking:** For persistent face IDs across frames, consider using `FaceTracker` instead

---

## Where Inference Runs: Deployment Options

Now that you understand model specs require an `inference_host_address`, let's explore the three options and when to use each.

### Cloud Inference (`@cloud`)
- **What:** DeGirum AI Hub in the cloud
- **When to use:** Experimenting with different hardware accelerators, no local hardware setup required
- **Pros:** All hardware types available, no installation needed, easy to switch between accelerators
- **Cons:** Requires internet connection, slight latency

```python
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"  # Run on DeGirum AI Hub
    )
)
```

### Local Inference (`@local`)
- **What:** Run models directly on your local edge device or workstation
- **When to use:** Production edge deployments, offline operation, low latency
- **Pros:** Lowest latency, data stays local
- **Cons:** Requires local hardware installation and drivers

```python
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="OPENVINO/NPU",
        inference_host_address="@local"  # Run on local Intel NPU
    )
)
```

### Remote AI Server (`"<host>:<port>"`)
- **What:** Connect to a remote AI inference server on your network
- **When to use:** Centralized inference for multiple clients, private cloud deployments
- **Pros:** Centralized GPU/accelerator resources, no per-client hardware needed
- **Cons:** Network dependency, requires server setup

```python
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="TENSORRT/GPU",
        inference_host_address="192.168.1.100:8778"  # Remote server
    )
)
```

**Server setup:** See the [AI Server Setup Guide](https://docs.degirum.com/pysdk/user-guide-pysdk/setting-up-an-ai-server) for instructions on deploying your own AI inference server.

**Recommended workflow:**
1. Start with `@cloud` to experiment and find the right hardware for your use case
2. Test your configuration and models
3. Switch to `@local` or remote server for production deployment

---

## Choosing Hardware: Discovery and Selection

Now that you understand where inference can run, let's explore what hardware accelerators are available and how to choose the right one for your use case.

### Step 1: See What's Supported

First, check what hardware types `degirum-face` knows about:

```python
import degirum_face

# What hardware types does the degirum-face registry support?
registry_hw = degirum_face.model_registry.get_hardware()
print(f"Supported in registry: {registry_hw}")
# Example output: ['HAILORT/HAILO8', 'N2X/ORCA1', 'OPENVINO/CPU', ...]
```

### Step 2: Check What's Available on Your Inference Host

Next, see what's actually available on the host you plan to use:

```python
# Check what's available on cloud
available_hw = degirum_face.get_system_hw("@cloud")
print(f"Available on @cloud: {available_hw}")

# Or check your local machine
local_hw = degirum_face.get_system_hw("@local")
print(f"Available locally: {local_hw}")
```

### Step 3: Find Compatible Hardware

Get the intersection of what's supported AND available:

```python
# What can I use right now?
compatible_hw = degirum_face.get_compatible_hw("@cloud")
print(f"Ready to use: {compatible_hw}")
```

---

## Configuring for Specific Hardware

Now that you've discovered available hardware, you can create custom configurations optimized for specific accelerators.

### Basic Pattern

All custom configurations follow this pattern:

1. **Choose your hardware and inference host**
2. **Get model specs** for that hardware using `get_face_detection_model_spec()` and `get_face_embedding_model_spec()`
3. **Create a config** with those specs
4. **Create the recognizer** with your config

### Example 1: Local Edge Deployment (Hailo-8)

Deploy face recognition on a Hailo-8 edge device:

```python
import degirum_face

# Specify target hardware and deployment location
DEVICE_TYPE = "HAILORT/HAILO8"
INFERENCE_HOST = "@local"  # Running on edge device

# Get optimized model specs for Hailo-8
face_detector_spec = degirum_face.get_face_detection_model_spec(
    device_type=DEVICE_TYPE,
    inference_host_address=INFERENCE_HOST,
)
face_embedding_spec = degirum_face.get_face_embedding_model_spec(
    device_type=DEVICE_TYPE,
    inference_host_address=INFERENCE_HOST,
)

# Create configuration
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=face_detector_spec,
    face_embedding_model_spec=face_embedding_spec,
    db_path="./face_db_hailo8.lance",
    cosine_similarity_threshold=0.6,
)

# Create recognizer
face_recognizer = degirum_face.FaceRecognizer(config)

# Now you can enroll and recognize as usual
face_recognizer.enroll_image('person.jpg', 'John Doe')
result = face_recognizer.predict('test.jpg')
```

**Important:** Note the database path `face_db_hailo8.lance` - use a separate database for each hardware type (explained in [Database Management](#database-management)).

### Example 2: Cloud Experimentation

Try different accelerators on the cloud without any local hardware setup:

```python
import degirum_face

# Test different hardware types on cloud
hardware_options = ["N2X/ORCA1", "HAILORT/HAILO8", "OPENVINO/NPU"]

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
    # Test inference speed, accuracy, etc. for your specific use case
```

This approach lets you compare performance across hardware before committing to a deployment.

---

## Using YAML Configuration Files

Instead of building `FaceRecognizerConfig` objects in Python code, you can **initialize them from YAML files**. This is especially useful for production deployments and team collaboration.

### Benefits of YAML Configuration

- **Cleaner than Python code** - Configuration is separated from application logic
- **Easy to modify** - Change hardware, thresholds, or filters without touching code
- **Version control friendly** - Track configuration changes independently in your repo
- **Shareable across team** - Everyone uses the same configuration file

### Step 1: Create a YAML Configuration File

Create a file named `face_config.yaml`:

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

# Optional: Face filtering configuration
face_filters:
  enable_small_face_filter: true
  min_face_size: 50
  enable_frontal_filter: true
  enable_shift_filter: true
```

The YAML structure mirrors the `FaceRecognizerConfig` structure, with all the same fields available.

### Step 2: Load Configuration from YAML

Use `FaceRecognizerConfig.from_yaml()` to create a config object from your YAML file:

```python
import degirum_face

# Initialize FaceRecognizerConfig from YAML file
config, settings = degirum_face.FaceRecognizerConfig.from_yaml(
    yaml_file="face_config.yaml"
)

# Create recognizer with the YAML-based config
face_recognizer = degirum_face.FaceRecognizer(config)

# Use normally - all configuration comes from YAML
face_recognizer.enroll_image('person.jpg', 'John Doe')
result = face_recognizer.predict('test.jpg')
```

**What gets returned:**
- `config` - A fully initialized `FaceRecognizerConfig` object ready to use
- `settings` - The raw dictionary loaded from YAML (useful for debugging)

### Alternative: Load from YAML String

You can also load configuration from a YAML string instead of a file:

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

**Recommendation:** For production deployments, store configurations in YAML files and load them at runtime. This makes it easy to maintain different configs for development, staging, and production environments.

See [examples/face_recognition.yaml](examples/face_recognition.yaml) for a complete working example.

---

## Face Filtering Configuration

Face filters act as **quality gates** that skip low-quality face detections before running the computationally expensive embedding model. Proper filtering improves both performance and accuracy.

### Why Use Face Filters?

Not every detected face should be processed:
- **Small/distant faces** - Too few pixels for reliable feature extraction
- **Profile/side views** - Embedding models work best on frontal faces
- **Poor framing** - Faces cut off at image edges produce unreliable embeddings
- **Redundant processing** - In video, don't re-embed the same tracked face every frame

Filters prevent these cases from wasting compute resources and polluting your results.

### FaceFilterConfig Overview

Face filtering is controlled by a `FaceFilterConfig` object that's part of `FaceRecognizerConfig`:

```python
import degirum_face

filter_config = degirum_face.FaceFilterConfig(
    # Small face filter
    enable_small_face_filter=True,
    min_face_size=50,
    
    # Zone filter (spatial constraint)
    enable_zone_filter=True,
    zone=[[100, 100], [500, 100], [500, 400], [100, 400]],
    
    # Geometric filters
    enable_frontal_filter=True,
    enable_shift_filter=True,
    
    # Temporal filter (for tracking/video)
    enable_reid_expiration_filter=True,
    reid_expiration_frames=10,
)

# Use in FaceRecognizerConfig
config = degirum_face.FaceRecognizerConfig(
    face_filters=filter_config,
    # ... other config fields
)
```

### Filter Types in Detail

#### 1. Small Face Filter

Skips faces where the bounding box is too small for reliable recognition.

```python
face_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=50  # Minimum size in pixels for the shorter side of bbox
)
```

**When to use:**
- Processing images with varying distances from camera
- Want to ignore distant/background people
- Improve accuracy by filtering unreliable small detections

**Trade-off:** Higher `min_face_size` = faster processing but may miss distant faces

#### 2. Zone Filter

Only processes faces within a specified polygon region.

```python
# Define a rectangular zone (top-left to bottom-right)
zone = [
    [100, 100],   # Top-left corner (x, y)
    [500, 100],   # Top-right corner
    [500, 400],   # Bottom-right corner
    [100, 400]    # Bottom-left corner
]

face_filters = degirum_face.FaceFilterConfig(
    enable_zone_filter=True,
    zone=zone  # List of [x, y] coordinates (minimum 3 points)
)
```

**When to use:**
- Focus recognition on specific areas (e.g., doorway, checkout counter)
- Ignore people outside region of interest
- Reduce false positives from background activity

**How it works:** Face center point must be inside the polygon zone

#### 3. Frontal Filter

Only processes faces looking roughly toward the camera (frontal view).

```python
face_filters = degirum_face.FaceFilterConfig(
    enable_frontal_filter=True
)
```

**When to use:**
- Need high-quality embeddings (frontal faces work best)
- Access control scenarios where users face the camera
- Reduce processing of profile/side views

**How it works:** Checks if nose keypoint is inside the rectangle formed by eyes and mouth

#### 4. Shift Filter

Skips faces that are poorly framed (cut off at image edges or off-center).

```python
face_filters = degirum_face.FaceFilterConfig(
    enable_shift_filter=True
)
```

**When to use:**
- Avoid processing partially visible faces
- Improve embedding quality by filtering edge cases
- Video scenarios where people enter/exit frame

**How it works:** Rejects faces where facial keypoints are clustered to one side of the bounding box

#### 5. ReID Expiration Filter

**Note:** The ReID expiration filter is specific to face tracking workflows and does not impact `FaceRecognizer`. This filter will be covered in detail in the face tracking guide.

### Combining Filters

Filters work together - a face must pass **all enabled filters** to be processed:

```python
# Strict filtering: frontal, properly sized faces in specific zone
strict_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=80,              # Larger minimum
    enable_frontal_filter=True,     # Must be frontal
    enable_shift_filter=True,       # Must be well-framed
    enable_zone_filter=True,        # Must be in zone
    zone=[[200, 150], [600, 150], [600, 450], [200, 450]]
)

# Permissive filtering: only skip very small faces
permissive_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=30,              # Lower threshold
    # All other filters disabled
)
```

### Using Filters in Configuration

Filters can be specified in both Python and YAML:

**Python:**
```python
import degirum_face

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec("TFLITE/CPU"),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec("TFLITE/CPU"),
    db_path="./face_db.lance",
    cosine_similarity_threshold=0.6,
    face_filters=degirum_face.FaceFilterConfig(
        enable_frontal_filter=True,
        enable_small_face_filter=True,
        min_face_size=60
    )
)
```

**YAML:**
```yaml
face_detector:
  hardware: TFLITE/CPU
  inference_host_address: "@local"
face_embedder:
  hardware: TFLITE/CPU
  inference_host_address: "@local"
db_path: ./face_db.lance
cosine_similarity_threshold: 0.6

face_filters:
  enable_frontal_filter: true
  enable_small_face_filter: true
  min_face_size: 60
```

### Filter Tuning Recommendations

**For Access Control / Security:**
- Enable frontal filter (ensure clear face view)
- Higher min_face_size (60-80 pixels, or even 200-400 pixels for maximum quality)
- For strict access control, set min_face_size to ~50% of frame height to ensure close-up enrollment
- Enable shift filter (avoid partial faces)
- Use zone filter for entry points

**For General Recognition:**
- Moderate min_face_size (40-50 pixels)
- Consider enabling frontal filter for better accuracy
- Zone filter optional based on use case

**For Maximum Coverage:**
- Lower min_face_size (30-40 pixels)
- Disable geometric filters (frontal, shift)
- Skip zone filtering


