# FaceTracker Methods

**Note:** Examples in this guide assume you have already configured `FaceTrackerConfig` with model specifications. See [Configuration Guide](configuration.md) for complete setup details.

## Methods Overview

| Method | Purpose | Use Case |
|--------|---------|----------|
| **`start_face_tracking_pipeline()`** | Real-time monitoring with automated alerting | Security surveillance, access control, live monitoring |
| **`predict_batch()`** | Stream processing with programmatic access | Custom analytics, logging, integration with other systems |
| **`find_faces_in_file()`** | Analyze local video files | Post-incident review, enrollment from footage |
| **`find_faces_in_clip()`** | Analyze cloud storage clips | Review alert clips, batch processing from S3 |
| **`enroll()`** | Add faces from video to database | Build database from video footage |

---

## start_face_tracking_pipeline()

Run continuous real-time video monitoring with automated alerting, clip recording, and live streaming.

**When to use:** This is the primary method for production deployments where you need a fully automated system that runs continuously, handles alerts, saves video clips, and sends notifications. While you can attach a custom `sink` to access results programmatically, the main value of this method is the automated handling—use `predict_batch()` if programmatic result processing is your primary goal.

### Signature

```python
start_face_tracking_pipeline(
    frame_iterator: Optional[Iterable] = None,
    sink: Optional[SinkGizmo] = None,
    sink_connection_point: str = "detector"
) -> Tuple[Composition, Watchdog]
```

### Parameters

- **`frame_iterator`** (Optional) - Custom frame source; if None, uses `config.video_source`
- **`sink`** (Optional) - Custom output sink for results
- **`sink_connection_point`** (str) - Where to attach the sink: `"detector"` (default) or `"recognizer"`

### Returns

- `Composition` - Pipeline composition object (call `.wait()` to run)
- `Watchdog` - Monitoring object for pipeline health

### Example: Security Monitoring

Monitor RTSP camera, save clips, and send notifications:

```python
import degirum_face
import degirum_tools

# Configure tracking with alerts and clip recording
config = degirum_face.FaceTrackerConfig(
    # ... model specs and database (see configuration guide) ...
    video_source="rtsp://192.168.1.100/stream",
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    clip_duration=150,
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    ),
    notification_config="mailto://security@company.com",
    notification_message="⚠️ Unknown person at ${time}",
    live_stream_mode="WEB",
    live_stream_rtsp_url="entrance_camera",
)

tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()
composition.wait()  # Run until Ctrl+C
```

### How the Pipeline Works

1. **Frame Acquisition** - Read frame from video source
2. **Face Detection** - Detect faces with landmarks
3. **Object Tracking** - Assign persistent track IDs
4. **Face Filtering** - Apply quality filters (small face, frontal, zone, shift, ReID expiration)
5. **Face Extraction** - Crop and align faces
6. **Embedding Extraction** - Generate embeddings (adaptive backoff via ReID filter)
7. **Database Search** - Match embeddings against enrolled faces
8. **Alert Evaluation** - Check credence count and alert mode
9. **Clip Recording** - Save video clips when alerts trigger
10. **Notification** - Send alerts via configured channels
11. **Live Streaming** - Output annotated video to display/RTSP

---

## predict_batch()

Process video streams and return inference results for each frame with programmatic access.

**When to use:** Use this when you need fine-grained control over the processing pipeline. Unlike `start_face_tracking_pipeline()`, this method gives you access to results for every frame, allowing you to implement custom logic, logging, integration with other systems, or build your own alerting mechanisms.

### Signature

```python
predict_batch(stream: Iterable) -> Iterator[InferenceResults]
```

### Parameters

- **`stream`** - Iterator yielding video frames as numpy arrays

### Returns

- Iterator of `InferenceResults` objects. InferenceResults objects support standard PySDK methods like `image_overlay()`, `results`, etc. See [InferenceResults documentation](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor)

Each result contains:
- `results` - List of detection dictionaries with tracking data (access via `result.results[i].get("track_id")`)
- `faces` property - List of `FaceRecognitionResult` objects. See [FaceRecognitionResult Reference](../../reference/face-recognition-result.md)

**Note:** Tracking data (`track_id`, `frame_id`) is in the `results` list, not as properties of `FaceRecognitionResult`. To correlate, use the same index for both lists.

### Example: Custom Logging

Process video and log all face detections:

```python
import cv2
import json
from datetime import datetime

def frame_generator():
    cap = cv2.VideoCapture("surveillance.mp4")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()

# Assumes tracker is already configured
with open("face_detections.jsonl", "w") as log_file:
    for result in tracker.predict_batch(frame_generator()):
        timestamp = datetime.now().isoformat()
        
        for i, face_dict in enumerate(result.results):
            face = result.faces[i]  # Get corresponding FaceRecognitionResult
            log_entry = {
                "timestamp": timestamp,
                "track_id": face_dict.get("track_id"),
                "person": face.attributes or "Unknown",
                "confidence": face.similarity_score,
                "bbox": face.bbox
            }
            log_file.write(json.dumps(log_entry) + "\n")
```

---

## find_faces_in_file()

Analyze local video files to find and track all faces, optionally creating annotated output.

**When to use:** This is the go-to method for offline analysis of recorded video. Use it for post-incident review, enrolling faces from existing footage, or batch processing local video files. The method automatically handles tracking, clusters similar faces, and produces annotated videos for easy review.

### Signature

```python
find_faces_in_file(
    file_path: str,
    save_annotated: bool = True,
    output_video_path: Optional[str] = None,
    compute_clusters: bool = True
) -> Dict[int, FaceAttributes]
```

### Parameters

- **`file_path`** (str) - Path to input video file
- **`save_annotated`** (bool) - Whether to save annotated video (default: True)
- **`output_video_path`** (Optional[str]) - Path for annotated output video
- **`compute_clusters`** (bool) - Whether to compute K-means clustering on embeddings (default: True)

### Returns

- `Dict[int, FaceAttributes]` - Dictionary mapping track IDs to face data:
  - Each `FaceAttributes` object contains embeddings and attributes (if recognized)
  - Track IDs are persistent across frames
  - Embeddings are clustered if `compute_clusters=True`

### Example: Review and Enroll

Analyze video, review faces, and enroll new people:

```python
# Assumes tracker is already configured with db_path

# Analyze video and save annotated version
faces = tracker.find_faces_in_file(
    file_path="lobby_camera_2026-01-02.mp4",
    save_annotated=True,
    output_video_path="lobby_annotated.mp4"
)

print(f"Found {len(faces)} unique individuals")

# Review and enroll unknown faces
for track_id, face_data in faces.items():
    if face_data.attributes is None:  # Unknown person
        print(f"\nTrack {track_id}: {len(face_data.embeddings)} samples")
        name = input("  Who is this? (Enter to skip): ")
        
        if name:
            face_data.attributes = name
            tracker.enroll(face_data)
            print(f"  ✅ Enrolled as {name}")
```

---

## find_faces_in_clip()

Analyze video clips from object storage (S3 or local), similar to `find_faces_in_file()` but for cloud/storage-based clips.

**When to use:** Use this to review video clips saved by `start_face_tracking_pipeline()` or stored in S3/object storage. It's particularly useful for reviewing alert clips generated by the automated pipeline, allowing you to verify detections and enroll faces from those incidents.

### Signature

```python
find_faces_in_clip(
    clip_object_name: str,
    save_annotated: bool = True,
    compute_clusters: bool = True
) -> Dict[int, FaceAttributes]
```

### Parameters

- **`clip_object_name`** (str) - Name of video clip in object storage
- **`save_annotated`** (bool) - Whether to save annotated video back to storage (default: True)
- **`compute_clusters`** (bool) - Whether to compute K-means clustering on embeddings (default: True)

### Returns

- `Dict[int, FaceAttributes]` - Dictionary mapping track IDs to face data (same as `find_faces_in_file()`)

### Requirements

- `clip_storage_config` must be configured in `FaceTrackerConfig`

### Example: Review Alert Clips

Process unknown person clips from cloud storage:

```python
import degirum_face

# Assumes tracker is configured with clip_storage_config

# List all clips
clip_manager = degirum_face.FaceClipManager(tracker.config.clip_storage_config)
clips = clip_manager.list_clips()

print(f"Found {len(clips)} clips to review")

# Analyze each clip
for clip_name in clips.keys():
    print(f"\nAnalyzing: {clip_name}")
    
    faces = tracker.find_faces_in_clip(
        clip_object_name=clip_name,
        save_annotated=True
    )
    
    print(f"  Found {len(faces)} unique individuals")
    
    for track_id, face_data in faces.items():
        if face_data.attributes is None:
            print(f"    Track {track_id}: UNKNOWN ({len(face_data.embeddings)} samples)")
```

**Note:** Annotated videos are saved with `_annotated` suffix in the same storage location.

---

## enroll()

Enroll face(s) into the database using embeddings extracted from video analysis.

**When to use:** Use this after analyzing videos with `find_faces_in_file()` or `find_faces_in_clip()` to add new individuals to your database. This approach leverages video footage to capture multiple angles and expressions, creating more robust face profiles than single-image enrollment.

### Signature

```python
enroll(face_list: Union[FaceAttributes, List[FaceAttributes]])
```

### Parameters

- **`face_list`** - Single `FaceAttributes` object or list of objects to enroll
  - Must have `attributes` property set (e.g., person name)
  - Must contain `embeddings` (populated by `find_faces_in_file()` or `find_faces_in_clip()`)

### Workflow

1. Run `find_faces_in_file()` or `find_faces_in_clip()` to extract faces
2. Assign `attributes` (person name) to each face you want to enroll
3. Call `enroll()` with the face data

### Example: Interactive Enrollment

```python
# Assumes tracker is already configured

# Extract faces from video
faces = tracker.find_faces_in_file("footage.mp4")

# Interactively enroll each face
for track_id, face_data in faces.items():
    print(f"\nTrack {track_id}: {len(face_data.embeddings)} samples")
    
    if face_data.attributes:
        print(f"  Already known: {face_data.attributes}")
    else:
        name = input("  Enter name (or press Enter to skip): ")
        if name:
            face_data.attributes = name
            tracker.enroll(face_data)
            print(f"  ✅ Enrolled as {name}")
```

**Notes:**
- Faces without `attributes` are skipped with a warning
- Each face can have multiple embeddings (from different frames/angles)
- K-means clustering reduces embeddings to representative samples
- More samples = better accuracy (recommended: 20+ frames)
