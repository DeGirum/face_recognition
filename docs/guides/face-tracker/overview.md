# FaceTracker Overview

## What is FaceTracker?

`FaceTracker` extends `FaceRecognizer` for **production video surveillance applications**. While `FaceRecognizer` processes individual images independently, `FaceTracker` adds persistent face tracking, automated alerting, video clip recording, and live streaming capabilities for continuous video monitoring.

## Key Differences from FaceRecognizer

| Capability | FaceRecognizer | FaceTracker |
|------------|----------------|-------------|
| **Identity persistence** | Each frame processed separately | Stable track IDs across frames |
| **Embedding extraction** | Every frame (redundant) | Adaptive backoff (10-20x reduction) |
| **Alerting** | Manual implementation required | Built-in modes with configurable triggers |
| **Video evidence** | Not supported | Automatic clip recording to S3/local |
| **Notifications** | Not supported | Integrated Apprise (email, Slack, SMS) |
| **Live streaming** | Not supported | Local display or RTSP web streaming |
| **Video post-processing** | Not supported | Extract and enroll faces from clips |

## When to Use FaceTracker

| Use Case | Recommended Class | Why |
|----------|------------------|-----|
| Real-time video streams | `FaceTracker` | Persistent track IDs, reduced re-embedding |
| Alerting on unknown faces | `FaceTracker` | Built-in alert modes and notifications |
| Clip recording | `FaceTracker` | Automatic video clip saving |
| Video with temporal consistency | `FaceTracker` | Maintains face identity across frames |
| Single images | `FaceRecognizer` | Simple, direct recognition |
| Batch of images | `FaceRecognizer` | Pipeline parallelism for throughput |

## Core Concepts

### FaceTrackerConfig

`FaceTrackerConfig` extends `FaceRecognizerConfig` and configures all aspects of video tracking. It inherits base settings (model specs, database path, similarity threshold, face filters) and adds tracking-specific parameters:

- **Video source** - Webcam, file, or RTSP stream
- **Credence count** - Frames required to confirm a face
- **Alert mode and notifications** - When and how to alert
- **Clip storage** - Save video clips to S3 or local storage
- **Live streaming** - Display output locally or via RTSP

See [Configuration Guide](configuration.md) for complete parameter reference and examples.

### Track IDs
Unlike `FaceRecognizer` which processes each frame independently, `FaceTracker` assigns persistent track IDs to faces as they move across frames. This enables:
- Reduced computational cost (avoid re-extracting embeddings for same person)
- Consistent identity throughout video
- Alert once per person (not per frame)

### Credence Count
Number of consecutive frames a face must appear before being confirmed as a valid track. Higher values reduce false positives from momentary detections or camera noise.

### Alert Modes
- `AlertMode.NONE` - No alerts
- `AlertMode.ON_UNKNOWNS` - Alert when unrecognized faces appear
- `AlertMode.ON_KNOWNS` - Alert when enrolled faces appear  
- `AlertMode.ON_ALL` - Alert for all faces

### Adaptive Re-identification
When the ReID expiration filter is enabled in face filters configuration, `FaceTracker` uses exponential backoff to reduce embedding extraction frequency for stable tracks. Instead of extracting embeddings every frame, the interval increases exponentially (1 → 2 → 4 → 8 → 16 → ...) up to the configured maximum `reid_expiration_frames`, improving performance 10-20x while maintaining accurate tracking. See [ReID Expiration Filter](configuration.md#reid-expiration-filter) for configuration details.

## Methods

`FaceTracker` provides specialized methods for different video processing workflows:

- **[start_face_tracking_pipeline()](methods.md#start_face_tracking_pipeline)** - Real-time monitoring with automated alerts and clip recording
- **[predict_batch()](methods.md#predict_batch)** - Stream processing with programmatic access to results
- **[find_faces_in_file()](methods.md#find_faces_in_file)** - Analyze local video files
- **[find_faces_in_clip()](methods.md#find_faces_in_clip)** - Analyze cloud storage clips
- **[enroll()](methods.md#enroll)** - Add faces from video to database
