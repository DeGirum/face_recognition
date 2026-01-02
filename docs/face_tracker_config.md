# FaceTracker Configuration Reference

Complete guide to all `FaceTrackerConfig` settings for production video surveillance applications.

## Overview

`FaceTrackerConfig` inherits from `FaceRecognizerConfig` and adds tracking-specific settings for continuous video monitoring.

### Configuration Inheritance

All FaceRecognizer settings apply:
- **Face detection model spec** - Which detection model and hardware
- **Face embedding model spec** - Which embedding model and hardware
- **Database path** - Where face embeddings are stored
- **Similarity threshold** - Matching confidence (0.0-1.0)
- **Face filters** - Quality gates (small face, frontal, zone, shift)

See the [FaceRecognizer Configuration Guide](face_recognizer.md#anatomy-of-facerecognizerconfig) for details on these inherited settings.

### Additional Tracking Settings

`FaceTracker` extends `FaceRecognizer` for **continuous video streams** with real-time monitoring capabilities. While `FaceRecognizer` processes individual images or batches, `FaceTracker` adds persistent tracking across frames, automated alerting when specific conditions are met, video clip recording for evidence, and live streaming for remote monitoring.

---

## Configuration Parameters

### 1. Video Source

Input video source and overrides for incorrect camera metadata.

**Parameters:**

- **`video_source`** - Input video source:
  - Integer (e.g., `0`, `1`) - Local webcam index
  - String path (e.g., `"video.mp4"`) - Video file
  - RTSP URL (e.g., `"rtsp://192.168.1.100/stream"`) - IP camera

- **`video_source_fps_override`** - Override frame rate when camera reports incorrect FPS (default: 0.0 = no override)

- **`video_source_resolution_override`** - Override resolution as `(width, height)` tuple when camera reports incorrect dimensions (default: (0, 0) = no override)

**Example:**
```python
config = degirum_face.FaceTrackerConfig(
    video_source="rtsp://192.168.1.100/stream",
    video_source_fps_override=30.0,  # Force 30 FPS
    video_source_resolution_override=(1920, 1080),  # Force 1080p
)
```

---

### 2. Face Tracking Confirmation

Controls when a detected face is "confirmed" for tracking and subsequent processing.

**Parameters:**

- **`credence_count`** - Number of consecutive frames a face must appear before being confirmed as a valid track. Reduces false positives from momentary detections, camera noise, or transient objects.

**Recommended values:**
- `2-4` - Real-time monitoring (quick confirmation)
- `5-10` - High-traffic areas (reduce false positives)
- `10+` - Critical security applications (maximum stability)

**Example:**
```python
config = degirum_face.FaceTrackerConfig(
    credence_count=6,  # Require 6 consecutive frames
)
```

---

### 3. Alerting and Notifications

Controls when and how alerts are triggered for confirmed faces, including notification delivery.

**Note:** Clip recording (see next section) only occurs when `alert_mode` is not `NONE`. Alerts trigger the video clip saving mechanism.

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

**Example:**
```python
config = degirum_face.FaceTrackerConfig(
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    alert_once=True,
    clip_duration=150,  # 5 seconds at 30 FPS
    notification_config="mailto://user:pass@gmail.com",
    notification_message="⚠️ ${time}: Unknown person detected. Video: ${filename}",
    notification_timeout_s=15.0,
)
```

**Apprise notification examples:**
- Email: `"mailto://user:pass@gmail.com"`
- Slack: `"slack://token/channel"`
- Discord: `"discord://webhook_id/webhook_token"`
- SMS (Twilio): `"twilio://account_sid:auth_token@from_phone/to_phone"`
- Console: `"console://"` (for testing)

See [Apprise documentation](https://github.com/caronc/apprise) for all supported services.

---

### 4. Clip Storage

**Important:** Clip storage only works when `alert_mode` is not `NONE`. Video clips are automatically saved when alerts are triggered.

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
    ),
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS  # Required for clip saving
)

# S3-compatible cloud storage
config = degirum_face.FaceTrackerConfig(
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="s3.amazonaws.com",
        access_key="YOUR_ACCESS_KEY",
        secret_key="YOUR_SECRET_KEY",
        bucket="face-tracking-clips",
        url_expiration_s=3600       # Optional: presigned URL expiration
    ),
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS  # Required for clip saving
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

**Clip saving behavior:**
- Clips are saved only when alerts are triggered (based on `alert_mode`)
- Clip length is controlled by `clip_duration` parameter (in frames)
- Each clip filename includes timestamp and trigger information

---

### 5. Live Stream Output

Configure live video streaming output.

**Parameters:**

- **`live_stream_mode`** - Live stream mode:
  - `"LOCAL"` - Display in local window
  - `"WEB"` - Stream via RTSP for web viewing
  - `"NONE"` - No live display

- **`live_stream_rtsp_url`** - RTSP URL path suffix (used when mode is `"WEB"`)

**Example:**
```python
# Local display
config = degirum_face.FaceTrackerConfig(
    live_stream_mode="LOCAL",
)

# Web streaming
config = degirum_face.FaceTrackerConfig(
    live_stream_mode="WEB",
    live_stream_rtsp_url="camera_entrance",  # rtsp://localhost:8554/camera_entrance
)

# No display (headless)
config = degirum_face.FaceTrackerConfig(
    live_stream_mode="NONE",
)
```

---

## ReID Expiration Filter

The **ReID Expiration Filter** is a tracking-specific face filter that uses **adaptive exponential backoff** to reduce how often face embeddings are extracted for continuously tracked faces.

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

## Python Configuration Example

Complete Python-based configuration (without YAML):

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

## Complete Example

Production-ready security monitoring system:

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
    
    # Clip storage
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknown_persons"
    ),
    
    # Notifications
    notification_config="mailto://security@company.com",
    notification_message="🚨 ${time}: Unknown person detected. Clip: ${filename}",
    notification_timeout_s=10.0,
    
    # Video source
    video_source="rtsp://192.168.1.100/stream",
    
    # Live display
    live_stream_mode="WEB",
    live_stream_rtsp_url="security_entrance",
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

**Next:** [Methods Guide](face_tracker_methods.md) - Learn about all FaceTracker methods and workflows
