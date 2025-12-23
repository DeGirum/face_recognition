# FaceTracker Guide

## Overview

`FaceTracker` is designed for **continuous video monitoring** applications where you need to:

- **Monitor live camera feeds** - Detect and identify faces in real-time from webcams, IP cameras, or RTSP streams
- **Track individuals across frames** - Maintain persistent identity as people move through the scene
- **Receive automated alerts** - Get notified when unknown persons appear or when specific individuals are detected
- **Record evidence clips** - Automatically save video clips when alert conditions are met
- **Stream annotated video** - Display or broadcast live video with face annotations and identity labels

**Real-world scenarios:**
- **Access control**: Alert when unauthorized persons approach secured areas
- **Security monitoring**: Track unknown individuals entering restricted zones
- **Attendance systems**: Identify and log known employees/students entering facilities
- **Customer analytics**: Count and track unique visitors in retail environments
- **Safety compliance**: Monitor for presence/absence of required personnel

Unlike `FaceRecognizer` which processes individual images or batches independently, `FaceTracker` maintains **temporal continuity** - tracking the same face across hundreds of frames, triggering alerts only when confidence thresholds are met, and optimizing compute by skipping redundant processing for tracked faces.

## Prerequisites

Before using FaceTracker, you should:
- Understand [FaceRecognizer](face_recognizer.md) concepts (configuration, methods, hardware selection)
- Know the basics of face detection, embedding, and database matching
- Have completed the FaceRecognizer examples
- Be familiar with video processing concepts (frame rates, streams, etc.)

## When to Use FaceTracker vs FaceRecognizer

| Use Case | Recommended Class | Why |
|----------|------------------|-----|
| Single images | `FaceRecognizer` | Simple, direct recognition |
| Batch of images | `FaceRecognizer` | Pipeline parallelism for throughput |
| Real-time video streams | `FaceTracker` | Persistent track IDs, reduced re-embedding |
| Alerting on unknown faces | `FaceTracker` | Built-in alert modes and notifications |
| Clip recording | `FaceTracker` | Automatic video clip saving |
| Video with temporal consistency | `FaceTracker` | Maintains face identity across frames |

**Key insight:** `FaceTracker` extends `FaceRecognizer` capabilities for continuous video streams by adding tracking, alerting, and clip management.

---

## Table of Contents
- [Understanding FaceTrackerConfig](#understanding-facetrackerconfig)
- [Python Configuration Example](#python-configuration-example)
- [YAML Configuration Structure](#yaml-configuration-structure)
- [FaceTracker Methods](#facetracker-methods)
- [ReID Expiration Filter](#reid-expiration-filter)
- [Complete Example](#complete-example)

---

## Understanding FaceTrackerConfig

`FaceTrackerConfig` inherits from `FaceRecognizerConfig` and adds tracking-specific settings.

### Inherited from FaceRecognizerConfig

All FaceRecognizer settings apply:
- **Face detection model spec** - Which detection model and hardware
- **Face embedding model spec** - Which embedding model and hardware
- **Database path** - Where face embeddings are stored
- **Similarity threshold** - Matching confidence (0.0-1.0)
- **Face filters** - Quality gates (small face, frontal, zone, shift)

See the [FaceRecognizer Configuration Guide](face_recognizer.md#anatomy-of-facerecognizerconfig) for details on these settings.

### Additional Tracking Settings

`FaceTracker` extends `FaceRecognizer` for **continuous video streams** with real-time monitoring capabilities. While `FaceRecognizer` processes individual images or batches, `FaceTracker` adds persistent tracking across frames, automated alerting when specific conditions are met, video clip recording for evidence, and live streaming for remote monitoring. These tracking-specific settings enable production-ready video surveillance and access control applications.

#### 1. Video Source

Input video source and overrides for incorrect camera metadata.

**Parameters:**

- **`video_source`** - Input video source:
  - Integer (e.g., `0`, `1`) - Local webcam index
  - String path (e.g., `"video.mp4"`) - Video file
  - RTSP URL (e.g., `"rtsp://192.168.1.100/stream"`) - IP camera

- **`video_source_fps_override`** - Override frame rate when camera reports incorrect FPS (default: 0.0 = no override)

- **`video_source_resolution_override`** - Override resolution as `(width, height)` tuple when camera reports incorrect dimensions (default: (0, 0) = no override)

#### 2. Clip Storage

Configuration for saving video clips to S3-compatible object storage or local filesystem.

**In Python:**

Storage is configured via the `clip_storage_config` parameter, which takes a `degirum_tools.ObjectStorageConfig` object:

```python
import degirum_tools

# Local filesystem storage
config = degirum_face.FaceTrackerConfig(
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./clips",        # Local directory path
        bucket="unknown_faces"      # Subdirectory name
    )
)

# S3-compatible cloud storage
config = degirum_face.FaceTrackerConfig(
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="s3.amazonaws.com",
        access_key="YOUR_ACCESS_KEY",
        secret_key="YOUR_SECRET_KEY",
        bucket="face-tracking-clips",
        url_expiration_s=3600       # Optional: presigned URL expiration
    )
)

# Disabled (default)
config = degirum_face.FaceTrackerConfig(
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="",
        bucket=""
    )
)
```

**ObjectStorageConfig parameters:**

- **`endpoint`** - S3-compatible storage endpoint URL (e.g., `s3.amazonaws.com`) or local directory path (e.g., `./clips`)
- **`access_key`** - Storage access key (not needed for local storage)
- **`secret_key`** - Storage secret key (not needed for local storage)
- **`bucket`** - Bucket name for S3 storage or subdirectory name for local storage
- **`url_expiration_s`** - Expiration time for presigned URLs (optional, S3 only)

**Storage modes:**
- **S3-compatible cloud storage** - Remote access, web dashboards, centralized multi-camera storage
- **Local filesystem** - Simple setup, no cloud dependencies, clips saved to local directory

**Storage disabled:** Leave `endpoint` or `bucket` empty to disable clip storage entirely.

#### 3. Face Tracking Confirmation

Fundamental setting that controls when a detected face is "confirmed" for tracking and subsequent processing.

**Parameters:**

- **`credence_count`** - Number of consecutive frames a face must appear before being confirmed as a valid track. Reduces false positives from momentary detections, camera noise, or transient objects. Higher values = more stable tracking but slower confirmation.

**Recommended values:**
- `2-4` - Real-time monitoring (quick confirmation)
- `5-10` - High-traffic areas (reduce false positives)
- `10+` - Critical security applications (maximum stability)

#### 4. Alerting and Notifications

Controls when and how alerts are triggered for confirmed faces, including clip recording and notification delivery.

**Parameters:**

- **`alert_mode`** - Controls when alerts are triggered:
  - `AlertMode.NONE` - No alerts
  - `AlertMode.ON_UNKNOWNS` - Alert when unknown face detected
  - `AlertMode.ON_KNOWNS` - Alert when known face detected
  - `AlertMode.ON_ALL` - Alert for all faces (known and unknown)

- **`alert_once`** - Whether to trigger alert only once per track or continuously:
  - `True` - Security/access control (one alert per person entry)
  - `False` - Continuous monitoring applications

- **`clip_duration`** - Length of video clips to save (in frames). Example: At 30 FPS, 100 frames = ~3.3 seconds of video.

- **`notification_config`** - Apprise configuration string for notification delivery (email, Slack, etc.)

- **`notification_message`** - Message template with variables: `${time}`, `${filename}`, `${url}`

- **`notification_timeout_s`** - Timeout in seconds for sending notifications

#### 5. Live Stream Output

Configure live video streaming output.

**Parameters:**

- **`live_stream_mode`** - Live stream mode:
  - `"LOCAL"` - Display in local window
  - `"WEB"` - Stream via RTSP for web viewing
  - `"NONE"` - No live display

- **`live_stream_rtsp_url`** - RTSP URL path suffix (used when mode is `"WEB"`)

---

## Python Configuration Example

For Python-based configuration (without YAML):

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceTrackerConfig(
    # Face detection model
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    
    # Face embedding model
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    
    # Database settings
    db_path="./face_tracking_db.lance",
    cosine_similarity_threshold=0.6,
    
    # Face filters
    face_filters=degirum_face.FaceFilterConfig(
        enable_small_face_filter=True,
        min_face_size=50,
        enable_zone_filter=False,
        zone=[],  # [[x1,y1], [x2,y2], [x3,y3]] for polygon
        enable_frontal_filter=True,
        enable_shift_filter=False,
        enable_reid_expiration_filter=True,
        reid_expiration_frames=30
    ),
    
    # Video source settings
    video_source=0,  # 0 for webcam, RTSP URL, or file path
    video_source_fps_override=0.0,  # 0 = use source FPS
    video_source_resolution_override=(0, 0),  # (0, 0) = use source resolution
    
    # Clip storage configuration
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="s3.amazonaws.com",  # Empty string to disable
        access_key="YOUR_ACCESS_KEY",
        secret_key="YOUR_SECRET_KEY",
        bucket="my-security-footage",
        url_expiration_s=3600
    ),
    
    # Face tracking confirmation
    credence_count=4,
    
    # Alerting and notifications
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,  # NONE, ON_UNKNOWNS, ON_KNOWNS, ON_ALL
    alert_once=True,
    clip_duration=100,
    notification_config="console://",  # Apprise notification URL
    notification_message="${time}: Unknown person detected. Video: [${filename}](${url})",
    notification_timeout_s=10,
    
    # Live streaming
    live_stream_mode="LOCAL",  # LOCAL, WEB, or NONE
    live_stream_rtsp_url="",
)

tracker = degirum_face.FaceTracker(config)
```

---

## YAML Configuration Structure

FaceTracker supports complete configuration via YAML files. Here's the complete structure with all parameter groups:

```yaml
# Complete FaceTracker YAML Configuration Structure

# Face detection model
face_detector:
  hardware: HAILORT/HAILO8                    # Runtime/device format
  inference_host_address: "@cloud"            # @cloud, @local, or AI server hostname
  model_zoo_url: degirum/hailo                # Optional: model zoo path
  token: your_token_here                      # Optional: cloud API token

# Face embedding model
face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"
  model_zoo_url: degirum/hailo

# Database settings
db_path: ./face_tracking_db.lance
cosine_similarity_threshold: 0.6

# Face filters (inherited from FaceRecognizer)
face_filters:
  enable_small_face_filter: true
  min_face_size: 50
  enable_zone_filter: false
  zone: [[x1,y1], [x2,y2], [x3,y3]]          # Polygon points (min 3)
  enable_frontal_filter: true
  enable_shift_filter: false
  enable_reid_expiration_filter: true
  reid_expiration_frames: 30

# Video source settings
video_source: 0                               # 0 for webcam, RTSP URL, or file path
video_source_fps_override: 0.0                # Override FPS (0 = use source FPS)
video_source_resolution_override: [0, 0]      # Override resolution (0 = use source)

# Clip storage configuration
storage:
  endpoint: ""                                # S3 endpoint (empty = disabled)
  access_key: ""                              # S3 access key
  secret_key: ""                              # S3 secret key
  bucket: ""                                  # S3 bucket name
  url_expiration_s: 3600                      # Presigned URL expiration

# Face tracking confirmation
credence_count: 4                             # Frames to confirm a face

# Alerting and notifications
alerts:
  alert_mode: ON_UNKNOWNS                     # NONE, ON_UNKNOWNS, ON_KNOWNS, ON_ALL
  alert_once: true                            # Alert once per track vs every frame
  clip_duration: 100                          # Clip length in frames
  notification_config: "console://"           # Apprise notification URL
  notification_message: "${time}: Unknown person detected. Video: [${filename}](${url})"
  notification_timeout_s: 10                  # Notification timeout (optional)

# Live streaming
live_stream:
  mode: LOCAL                                 # LOCAL, WEB, or NONE
  rtsp_url: face_tracking                     # RTSP path suffix (for WEB mode)
```

**Loading from YAML:**

```python
import degirum_face

config, _ = degirum_face.FaceTrackerConfig.from_yaml(yaml_file="face_tracking.yaml")
tracker = degirum_face.FaceTracker(config)
```

---

## FaceTracker Methods

`FaceTracker` has one primary method: `start_face_tracking_pipeline()`.

### start_face_tracking_pipeline()

Starts the face tracking pipeline for continuous video processing.

**Signature:**
```python
start_face_tracking_pipeline(
    frame_iterator: Optional[Iterable] = None,
    sink: Optional[SinkGizmo] = None
) -> Tuple[Composition, Watchdog]
```

**Parameters:**
- `frame_iterator` (Optional) - Custom frame source; if None, uses `config.video_source`
- `sink` (Optional) - Custom output sink for results

**Returns:**
- `Composition` - Pipeline composition object (call `.wait()` to run)
- `Watchdog` - Monitoring object for pipeline health

**Example 1: Basic Tracking with Local Display**

```python
import degirum_face

# Configure for webcam tracking
config = degirum_face.FaceTrackerConfig(
    video_source=0,  # Webcam
    live_stream_mode="LOCAL",  # Display locally
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
)

# Create tracker
tracker = degirum_face.FaceTracker(config)

# Start pipeline
composition, watchdog = tracker.start_face_tracking_pipeline()

# Run until user stops (Ctrl+C)
composition.wait()
```

**Example 2: Tracking with Custom Frame Source**

```python
import degirum_face
import cv2

def custom_frame_generator():
    """Generate frames from custom source"""
    cap = cv2.VideoCapture("custom_video.mp4")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()

config = degirum_face.FaceTrackerConfig(
    live_stream_mode="LOCAL",
)

tracker = degirum_face.FaceTracker(config)

# Use custom frame source
composition, watchdog = tracker.start_face_tracking_pipeline(
    frame_iterator=custom_frame_generator()
)

composition.wait()
```

**Example 3: RTSP Camera with Web Streaming**

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    video_source="rtsp://192.168.1.100/stream",  # RTSP camera
    live_stream_mode="WEB",  # Stream to web
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    notification_config="mailto://user:pass@gmail.com",
)

tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()

composition.wait()
```

### What Happens in the Pipeline

The face tracking pipeline performs these steps for each frame:

1. **Frame Acquisition** - Read frame from video source
2. **Face Detection** - Detect faces in frame
3. **Object Tracking** - Assign persistent track IDs to faces
4. **Face Filtering** - Apply quality filters (small face, frontal, zone, shift, ReID expiration)
5. **Face Extraction** - Crop and align faces
6. **Embedding Extraction** - Generate face embeddings (only when ReID expiration allows)
7. **Database Search** - Match embeddings against enrolled faces
8. **Alert Evaluation** - Check if alert conditions met (credence count, alert mode)
9. **Clip Recording** - Save video clips when alerts trigger
10. **Notification** - Send alerts via configured channels
11. **Live Streaming** - Output annotated video to display/RTSP

**Key advantage:** Track IDs persist across frames, reducing redundant embedding calculations via the ReID expiration filter.

---

## ReID Expiration Filter

The **ReID Expiration Filter** is a tracking-specific filter that uses **adaptive exponential backoff** to reduce how often face embeddings are extracted for continuously tracked faces.

### How It Works

When tracking a face across video frames, the system assigns a persistent track ID. The filter adaptively increases the interval between embedding extractions for stable tracks:

**Without ReID expiration filter:**
```
Frame 1: Detect face (track_id=5) → Extract embedding
Frame 2: Detect face (track_id=5) → Extract embedding
Frame 3: Detect face (track_id=5) → Extract embedding
Frame 4: Detect face (track_id=5) → Extract embedding
...every frame extracts embedding
```

**With ReID expiration enabled (reid_expiration_frames=30):**
```
Frame 1:  New face detected → Extract embedding
Frame 2:  Same face → Extract embedding (interval: 1 frame)
Frame 4:  Same face → Extract embedding (interval: 2 frames)
Frame 8:  Same face → Extract embedding (interval: 4 frames)
Frame 16: Same face → Extract embedding (interval: 8 frames)
Frame 32: Same face → Extract embedding (interval: 16 frames)
Frame 62: Same face → Extract embedding (interval: 30 frames, maxed out)
Frame 92: Same face → Extract embedding (interval: 30 frames)
...stays at 30 frame intervals
```

**How the interval grows:**
- Starts at 1 frame for new faces
- **Doubles each time**: 1 → 2 → 4 → 8 → 16 → ...
- **Caps at reid_expiration_frames** (e.g., 30)
- Stays at maximum interval for stable tracks

**Result:** For a face tracked over 100 frames, extracts ~7 embeddings instead of 100 (14x reduction).

### Configuration

```python
config = degirum_face.FaceTrackerConfig(
    face_filters=degirum_face.FaceFilterConfig(
        enable_reid_expiration_filter=True,
        reid_expiration_frames=30  # Maximum interval between embeddings
    )
)
```

**In YAML:**
```yaml
face_filters:
  enable_reid_expiration_filter: true
  reid_expiration_frames: 30  # Maximum interval
```

### Tuning reid_expiration_frames

This parameter sets the **maximum interval** (in frames) between embedding extractions for stable tracks:

**Static scenes (office entry, security checkpoint):**
```python
reid_expiration_frames=60  # Maximum 60 frames (~2 sec at 30 FPS)
# Stable faces, infrequent angle changes, can wait longer between embeddings
```

**Dynamic scenes (retail, crowded areas):**
```python
reid_expiration_frames=15  # Maximum 15 frames (~0.5 sec at 30 FPS)
# People move quickly, angles change often, need more frequent embeddings
```

**Trade-off:**
- **Higher value** = Longer maximum intervals, fewer embeddings, faster FPS, but slower to detect face angle changes
- **Lower value** = Shorter maximum intervals, more embeddings, slower FPS, but quicker response to face movement

**Recommended:** 30 frames (1 second at 30 FPS)

### When Embedding Extraction Happens

Embedding is extracted in these cases:
- **New track detected** - First embedding needed to establish identity
- **Expiration timer reached** - Based on adaptive interval (1, 2, 4, 8... up to max)
- **Track ID re-acquired** - After track was lost, fresh embedding needed
- **Quality filters passed after previous failure** - Retry when face quality improves

### Impact on FaceRecognizer

**Important:** ReID expiration filter has **no effect** on `FaceRecognizer.predict_batch()` because:
- No persistent track IDs across batch items  
- Each image processed independently
- No temporal continuity to build adaptive intervals

**Use only with FaceTracker** for real-time video streams with continuous tracking.

---

## Complete Example

Putting it all together:

```python
import degirum_face
import degirum_tools

# Configure face tracker
config = degirum_face.FaceTrackerConfig(
    # Models and hardware
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    
    # Database and matching
    db_path="./security_face_db.lance",
    cosine_similarity_threshold=0.65,
    
    # Face quality filters
    face_filters=degirum_face.FaceFilterConfig(
        enable_small_face_filter=True,
        min_face_size=80,
        enable_frontal_filter=True,
        enable_shift_filter=True,
        enable_reid_expiration_filter=True,
        reid_expiration_frames=30,
    ),
    
    # Tracking and alerting
    credence_count=4,
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    alert_once=True,
    clip_duration=100,
    
    # Notifications
    notification_config="mailto://security@company.com",
    notification_message="🚨 ${time}: Unknown person detected. Clip: ${filename}",
    notification_timeout_s=10.0,
    
    # Video source
    video_source="rtsp://192.168.1.100/stream",
    
    # Live display
    live_stream_mode="WEB",
    live_stream_rtsp_url="rtsp://username@password:ip:port",
)

# Start tracking
tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()

# Run continuously
print("Face tracking started. Press Ctrl+C to stop.")
composition.wait()
```

This configuration:
- ✅ Tracks faces from RTSP camera
- ✅ Uses Hailo-8 hardware for acceleration
- ✅ Filters low-quality faces (small, profile, shifted)
- ✅ Reduces compute with ReID expiration (30 frames)
- ✅ Alerts on unknown faces after 4 frame confirmation
- ✅ Saves 100-frame clips of unknown faces
- ✅ Sends email notifications
- ✅ Streams annotated video to web

---

