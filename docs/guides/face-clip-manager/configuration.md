# FaceClipManager Configuration

## Configuration Overview

`FaceClipManager` uses `ObjectStorageConfig` from `degirum_tools`. In typical usage, you reuse the same config from your FaceTracker setup:

```python
# Configure FaceTracker with clip storage
tracker_config = degirum_face.FaceTrackerConfig(
    # ... other settings ...
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    )
)

tracker = degirum_face.FaceTracker(tracker_config)

# Use same config for FaceClipManager
clip_manager = degirum_face.FaceClipManager(tracker_config.clip_storage_config)
```

For complete `ObjectStorageConfig` parameters and examples (AWS S3, MinIO, local storage), see:

**[Object Storage Configuration Reference](../../reference/storage-config.md)**

---

## Configuration Patterns

### Standalone Configuration

Create FaceClipManager with its own storage configuration:

```python
import degirum_face
import degirum_tools

clip_manager = degirum_face.FaceClipManager(
    degirum_tools.ObjectStorageConfig(
        endpoint="./clips",
        bucket="alerts"
    )
)
```

### Reuse FaceTracker Configuration

Typical pattern - use the same storage config as FaceTracker:

```python
import degirum_face
import degirum_tools

# Configure FaceTracker with clip storage
tracker_config = degirum_face.FaceTrackerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    db_path="./security_db.lance",
    video_source="rtsp://camera/stream",
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    clip_duration=150,
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    )
)

tracker = degirum_face.FaceTracker(tracker_config)

# Create FaceClipManager using same storage config
clip_manager = degirum_face.FaceClipManager(tracker_config.clip_storage_config)
```

See [Methods Reference](methods.md) for clip management operations.
