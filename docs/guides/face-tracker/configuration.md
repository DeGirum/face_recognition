# FaceTracker Configuration

## Configuration Inheritance

`FaceTrackerConfig` extends `FaceRecognizerConfig` and inherits all base settings:

- **Model specifications** - Face detection and embedding models (device_type, inference_host_address)
- **Database path** - Where face embeddings are stored  
- **Similarity threshold** - Matching confidence (0.0-1.0)
- **Read consistency interval** - Multi-process database synchronization (optional)
- **Face filters** - Quality gates (small face, frontal, zone, shift)

See [FaceRecognizer Configuration](../face-recognizer/configuration.md) for details on these settings.

---

## Configuration Parameters

FaceTracker adds the following tracking-specific parameters:

### Video Source

**Parameters:**

- **`video_source`** - Input video source (default: 0 for first webcam):
  - Integer (e.g., `0`, `1`) - Local webcam index
  - String path (e.g., `"video.mp4"`) - Video file
  - RTSP URL (e.g., `"rtsp://192.168.1.100/stream"`) - IP camera

- **`video_source_fps_override`** (optional) - Override frame rate when camera reports incorrect FPS (default: 0.0 = no override)

- **`video_source_resolution_override`** (optional) - Override resolution as `(width, height)` tuple when camera reports incorrect dimensions (default: (0, 0) = no override)

---

### Credence Count

Controls when a detected face is confirmed as a valid track for processing.

**Parameter:**

- **`credence_count`** - Number of consecutive frames a face must appear before being confirmed (default: 1). Reduces false positives from momentary detections or camera noise.

**Recommended values:**
- `2-4` - Real-time monitoring (quick confirmation)
- `5-10` - High-traffic areas (reduce false positives)
- `10+` - Critical security applications (maximum stability)

---

### Alert Mode and Notifications

Controls when alerts are triggered and how notifications are delivered.

**Parameters:**

- **`alert_mode`** - When to trigger alerts (default: AlertMode.NONE):
  - `AlertMode.NONE` - No alerts
  - `AlertMode.ON_UNKNOWNS` - Alert when unknown face detected
  - `AlertMode.ON_KNOWNS` - Alert when known face detected
  - `AlertMode.ON_ALL` - Alert for all faces

- **`alert_once`** (bool) - Alert once per track (True) or every time attributes change for the given track ID (False) (default: True)

- **`clip_duration`** (int) - Length of video clips in frames (default: 0 = no recording, e.g., 100 frames ≈ 3.3 seconds at 30 FPS)

- **`notification_config`** (str) - Apprise configuration string for notification delivery

- **`notification_message`** (str) - Message template with variables: `${time}`, `${filename}`, `${url}`

- **`notification_timeout_s`** (float, optional) - Timeout in seconds for sending notifications

**Apprise notification examples:**
- Email: `"mailto://user:pass@gmail.com"`
- Slack: `"slack://token/channel"`
- Discord: `"discord://webhook_id/webhook_token"`
- SMS (Twilio): `"twilio://account_sid:auth_token@from_phone/to_phone"`
- Console: `"console://"` (testing)

See [Apprise documentation](https://github.com/caronc/apprise) for all supported services.

---

### Clip Storage

Configuration for saving video clips to S3-compatible storage or local filesystem.

See [Object Storage Configuration Reference](../../reference/storage-config.md) for complete documentation including:
- Parameters (endpoint, bucket, access_key, etc.)
- Storage backend examples (AWS S3, MinIO, local filesystem)
- Environment-specific configurations
- Best practices

---

### Alerting and Storage Combinations

**Important:** Both notifications and clip recording only trigger when alerts are generated. If `alert_mode=AlertMode.NONE`, no alerts are generated, so notifications and clip recording will not happen even if configured.

| Alert Mode | Notifications | Clip Recording | Configuration |
|------------|---------------|----------------|---------------|
| Not `NONE` | ✅ Enabled | ✅ Enabled | Set `notification_config` + configure `clip_storage_config` with endpoint/bucket |
| Not `NONE` | ✅ Enabled | ❌ Disabled | Set `notification_config` + leave `clip_storage_config` endpoint/bucket empty |
| Not `NONE` | ❌ Disabled | ✅ Enabled | Leave `notification_config` empty + configure `clip_storage_config` with endpoint/bucket |
| Not `NONE` | ❌ Disabled | ❌ Disabled | Leave `notification_config` empty + leave `clip_storage_config` endpoint/bucket empty |
| `NONE` | ❌ Disabled | ❌ Disabled | No alerts generated - notifications and storage disabled regardless of configuration |

---

### Live Streaming

Controls video output display.

**Parameters:**

- **`live_stream_mode`** - Output mode:
  - `"LOCAL"` - Display in local window
  - `"WEB"` - Stream via RTSP for web viewing
  - `"NONE"` - No live display

- **`live_stream_rtsp_url`** (str, optional) - RTSP URL path suffix (used when mode is `"WEB"`)

---

### ReID Expiration Filter

Tracking-specific filter that reduces embedding extraction frequency using adaptive exponential backoff. When enabled, the interval between embedding extractions increases exponentially (1 → 2 → 4 → 8 → ...) up to the configured `reid_expiration_frames` maximum, improving performance 10-20x while maintaining accuracy.

Configured via `face_filters` parameter:
- **`enable_reid_expiration_filter`** - Enable/disable (default: False)
- **`reid_expiration_frames`** - Maximum interval in frames (default: 10)

See [ReID Expiration Filter](../../reference/face-filters.md#5-reid-expiration-filter) for complete documentation including tuning guidance and examples.

---

## Configuration Options

### Option 1: Python Configuration

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceTrackerConfig(
    # Models (using model registry)
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    
    # Database
    db_path="./face_tracking_db.lance",
    cosine_similarity_threshold=0.65,
    
    # Face filters
    face_filters=degirum_face.FaceFilterConfig(
        enable_small_face_filter=True,
        min_face_size=80,
        enable_frontal_filter=True,
        enable_shift_filter=True,
        enable_reid_expiration_filter=True,
        reid_expiration_frames=30,
    ),
    
    # Video source
    video_source="rtsp://192.168.1.100/stream",
    
    # Tracking
    credence_count=4,
    
    # Alerting
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    alert_once=True,
    clip_duration=100,
    
    # Clip storage (directory must exist before running)
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknown_persons"
    ),
    
    # Notifications
    notification_config="mailto://security@company.com",
    notification_message="🚨 ${time}: Unknown person. Clip: ${filename}",
    notification_timeout_s=10.0,
    
    # Live display
    live_stream_mode="WEB",
    live_stream_rtsp_url="security_entrance",
)

# Create the storage directory if it doesn't exist (for local storage)
from pathlib import Path
Path("./security_clips").mkdir(parents=True, exist_ok=True)

tracker = degirum_face.FaceTracker(config)
```

### Option 2: YAML Configuration

`FaceTrackerConfig` can be initialized from a YAML file or string using the `from_yaml()` method. This approach separates configuration from code, making it easier to version control settings, share configurations across teams, and maintain different configs for development, staging, and production environments.

**Complete YAML structure:**

```yaml
# Face detection model
face_detector:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"
  
# Face embedding model
face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"

# Database settings
db_path: ./face_tracking_db.lance
cosine_similarity_threshold: 0.65

# Face filters
face_filters:
  enable_small_face_filter: true
  min_face_size: 80
  enable_frontal_filter: true
  enable_shift_filter: true
  enable_reid_expiration_filter: true
  reid_expiration_frames: 30

# Video source
video_source: "rtsp://192.168.1.100/stream"
video_source_fps_override: 0.0              # 0 = use source FPS (no override)
video_source_resolution_override: [0, 0]    # [0, 0] = use source resolution (no override)

# Tracking
credence_count: 4

# Alerting
alerts:
  alert_mode: ON_UNKNOWNS                   # NONE, ON_UNKNOWNS, ON_KNOWNS, ON_ALL
  alert_once: true
  clip_duration: 100
  notification_config: "mailto://security@company.com"
  notification_message: "🚨 ${time}: Unknown person. Clip: ${filename}"
  notification_timeout_s: 10.0

# Clip storage
storage:
  endpoint: "./security_clips"              # IMPORTANT: Directory must exist before running
  access_key: ""
  secret_key: ""
  bucket: "unknown_persons"
  url_expiration_s: 3600

# Live streaming
live_stream:
  mode: WEB                                 # LOCAL, WEB, NONE
  rtsp_url: "security_entrance"
```

#### Loading from YAML

```python
import degirum_face

config, _ = degirum_face.FaceTrackerConfig.from_yaml(yaml_file="face_tracking.yaml")
tracker = degirum_face.FaceTracker(config)
```

**Returns:**
- `config` - Initialized `FaceTrackerConfig` object
- `settings` - Raw dictionary (useful for debugging)

#### Loading from YAML String

```python
import degirum_face

yaml_string = """
face_detector:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"
face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"
db_path: ./face_tracking_db.lance
video_source: 0
alerts:
  alert_mode: ON_UNKNOWNS
"""

config, _ = degirum_face.FaceTrackerConfig.from_yaml(yaml_str=yaml_string)
tracker = degirum_face.FaceTracker(config)
```

#### Benefits of YAML

- **Clean separation** - Config separate from code
- **Easy modification** - Change hardware without editing code
- **Version control** - Track config changes in git
- **Team collaboration** - Share standardized configs
- **Multiple environments** - dev.yaml, staging.yaml, prod.yaml

---

## Configuration Examples

### Example 1: Security Monitoring

Monitor RTSP camera, alert on unknown faces, save clips, send email:

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceTrackerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    db_path="./security_db.lance",
    cosine_similarity_threshold=0.65,
    video_source="rtsp://192.168.1.100/stream",
    credence_count=4,
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    alert_once=True,
    clip_duration=150,
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    ),
    notification_config="mailto://security@company.com",
    notification_message="⚠️ Unknown person at ${time}",
    live_stream_mode="WEB",
    live_stream_rtsp_url="security_feed",
)

tracker = degirum_face.FaceTracker(config)
```

### Example 2: VIP Access Control

Alert when known VIPs appear, display locally:

```python
config = degirum_face.FaceTrackerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    db_path="./vip_database.lance",
    video_source=0,  # Webcam
    alert_mode=degirum_face.AlertMode.ON_KNOWNS,
    notification_config="slack://token/channel",
    notification_message="VIP arrived: ${attributes}",
    live_stream_mode="LOCAL",
)

tracker = degirum_face.FaceTracker(config)
```

### Example 3: High-Traffic Filtering

Reduce false positives with strict quality filters:

```python
config = degirum_face.FaceTrackerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    db_path="./retail_db.lance",
    face_filters=degirum_face.FaceFilterConfig(
        enable_small_face_filter=True,
        min_face_size=100,  # Larger minimum
        enable_frontal_filter=True,
        enable_shift_filter=True,
        enable_reid_expiration_filter=True,
        reid_expiration_frames=15,  # More frequent for dynamic scene
    ),
    video_source="rtsp://retail-camera/stream",
    credence_count=8,  # Higher confirmation threshold
    alert_mode=degirum_face.AlertMode.ON_ALL,
    live_stream_mode="LOCAL",
)

tracker = degirum_face.FaceTracker(config)
```

---

## Troubleshooting

### "Path not allowed" Error

**Problem:** Getting "path not allowed" error when using local storage endpoint.

**Cause:** The local directory specified in `storage.endpoint` doesn't exist. When the path doesn't exist, the system treats it as an S3 bucket endpoint and validation fails.

**Solution:** Create the directory before running the tracker:

```python
from pathlib import Path

# Create storage directory
storage_path = Path("./security_clips")
storage_path.mkdir(parents=True, exist_ok=True)

# Then configure tracker
config = degirum_face.FaceTrackerConfig(
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="alerts"
    ),
    # ... other settings
)
```

Or in your shell before running:
```bash
mkdir -p ./security_clips
```

See [Object Storage Configuration Reference](../../reference/storage-config.md) for more details.
