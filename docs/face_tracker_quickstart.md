# FaceTracker Quick Start Guide

## What is FaceTracker?

`FaceTracker` extends `FaceRecognizer` for **production video surveillance applications**. While `FaceRecognizer` excels at processing individual images independently, `FaceTracker` adds critical capabilities for real-world monitoring systems.

### Key Differences from FaceRecognizer

| Capability | FaceRecognizer | FaceTracker |
|------------|----------------|-------------|
| **Identity persistence** | Each frame processed separately | Stable track IDs across frames |
| **Embedding extraction** | Every frame (redundant) | Adaptive backoff (10-20x reduction) |
| **Alerting** | Manual implementation required | Built-in modes with credence thresholds |
| **Video evidence** | Not supported | Automatic clip recording to S3/local |
| **Notifications** | Not supported | Integrated Apprise (email, Slack, SMS) |
| **Live streaming** | Not supported | Local display or RTSP web streaming |
| **Video post-processing** | Not supported | Extract and enroll faces from clips |

### When to Use FaceTracker vs FaceRecognizer

| Use Case | Recommended Class | Why |
|----------|------------------|-----|
| Single images | `FaceRecognizer` | Simple, direct recognition |
| Batch of images | `FaceRecognizer` | Pipeline parallelism for throughput |
| Real-time video streams | `FaceTracker` | Persistent track IDs, reduced re-embedding |
| Alerting on unknown faces | `FaceTracker` | Built-in alert modes and notifications |
| Clip recording | `FaceTracker` | Automatic video clip saving |
| Video with temporal consistency | `FaceTracker` | Maintains face identity across frames |

## Prerequisites

Before using FaceTracker:
- Understand [FaceRecognizer](face_recognizer.md) concepts (configuration, methods, hardware selection)
- Know the basics of face detection, embedding, and database matching
- Have completed the FaceRecognizer examples
- Be familiar with video processing concepts (frame rates, streams, etc.)

## Simple Example: Real-Time Webcam Monitoring

This example shows real-time face tracking with local display and alerts for unknown persons:

```python
import degirum_face

# Create configuration
config = degirum_face.FaceTrackerConfig(
    # Models (using cloud AI server)
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    
    # Database
    db_path="./face_database.lance",
    cosine_similarity_threshold=0.6,
    
    # Video source
    video_source=0,  # Webcam
    
    # Tracking settings
    credence_count=4,  # Confirm face after 4 frames
    
    # Alerting
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,  # Alert on unknown faces
    alert_once=True,  # One alert per person
    
    # Display
    live_stream_mode="LOCAL",  # Show video window
)

# Create tracker and start
tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()

# Run until Ctrl+C
print("Face tracking started. Press Ctrl+C to stop.")
composition.wait()
```

**What this does:**
- ✅ Monitors webcam in real-time
- ✅ Tracks faces with persistent IDs
- ✅ Alerts when unknown persons appear
- ✅ Displays annotated video locally
- ✅ Reduces compute with adaptive re-identification

## Common Use Cases

### 1. Security Monitoring with Clip Recording

Alert and save clips when unknown persons are detected:

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
    
    # RTSP camera
    video_source="rtsp://192.168.1.100/stream",
    
    # Alert on unknowns
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    clip_duration=100,  # 100 frames (~3 seconds at 30 FPS)
    
    # Save clips to local storage
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    ),
    
    # Email notifications
    notification_config="mailto://security@company.com",
    notification_message="⚠️ Unknown person detected at ${time}",
    
    live_stream_mode="WEB",
    live_stream_rtsp_url="security_feed",
)

tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()
composition.wait()
```

### 2. Access Control - Alert on Known VIPs

Alert when specific enrolled individuals are detected:

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
    video_source=0,
    
    # Alert when known persons appear
    alert_mode=degirum_face.AlertMode.ON_KNOWNS,
    notification_config="slack://token/channel",
    notification_message="VIP ${attributes} has arrived!",
    
    live_stream_mode="LOCAL",
)

tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()
composition.wait()
```

## Next Steps

- **[Configuration Reference](face_tracker_config.md)** - Detailed configuration options and advanced settings
- **[Methods Guide](face_tracker_methods.md)** - All FaceTracker methods with use cases and examples
- **[FaceRecognizer Guide](face_recognizer.md)** - Batch image processing without tracking

## Key Concepts

### Tracking vs Recognition
- **Recognition** (FaceRecognizer) - Identify faces in individual images
- **Tracking** (FaceTracker) - Follow the same face across video frames with persistent IDs

### Credence Count
Number of consecutive frames a face must appear before being confirmed. Higher values reduce false positives but slow down confirmation.

### Alert Modes
- `NONE` - No alerts
- `ON_UNKNOWNS` - Alert when unrecognized faces appear
- `ON_KNOWNS` - Alert when enrolled faces appear
- `ON_ALL` - Alert for all faces

### Adaptive Re-identification
FaceTracker uses exponential backoff to reduce embedding extraction frequency for stable tracks (from every frame to every 30 frames), improving performance 10-20x.

---

**Ready to dive deeper?** Check out the [Configuration Reference](face_tracker_config.md) for all available settings.
