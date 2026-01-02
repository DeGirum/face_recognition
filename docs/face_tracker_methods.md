# FaceTracker Methods Guide

Complete reference for all `FaceTracker` methods with use cases, workflows, and examples.

## Overview

`FaceTracker` provides five methods for different video processing workflows:

| Method | Purpose | When to Use |
|--------|---------|-------------|
| **`start_face_tracking_pipeline()`** | Real-time monitoring with alerts | Security surveillance, access control, live monitoring |
| **`predict_batch()`** | Stream processing with programmatic access | Custom analysis, logging, integration with other systems |
| **`find_faces_in_file()`** | Analyze local video files | Post-incident review, enrollment from footage, clip analysis |
| **`find_faces_in_clip()`** | Analyze cloud storage clips | Review alert clips, batch processing from S3 |
| **`enroll()`** | Add faces to database | Build database from video footage, enroll from clips |

---

## Method Selection Guide

Use this decision tree to choose the right method:

```
Do you need real-time monitoring with alerts?
├─ YES → start_face_tracking_pipeline()
│   ├─ Need clip recording? → Configure clip_storage_config + alert_mode
│   └─ Need notifications? → Configure notification_config
│
└─ NO → Processing pre-recorded video?
    ├─ YES → Video is local file?
    │   ├─ YES → find_faces_in_file()
    │   └─ NO (in cloud/S3) → find_faces_in_clip()
    │
    └─ NO → Need programmatic access to results?
        ├─ YES → predict_batch()
        └─ NO → Building face database?
            └─ YES → find_faces_in_file() + enroll()
```

---

## Methods Reference

### start_face_tracking_pipeline()

**Purpose:** Run continuous real-time video monitoring with automated alerting, clip recording, and live streaming.

**When to use:**
- Security surveillance systems
- Access control applications
- Real-time unknown person detection
- Automated incident recording

**Signature:**
```python
start_face_tracking_pipeline(
    frame_iterator: Optional[Iterable] = None,
    sink: Optional[SinkGizmo] = None,
    sink_connection_point: str = "detector"
) -> Tuple[Composition, Watchdog]
```

**Parameters:**
- `frame_iterator` (Optional) - Custom frame source; if None, uses `config.video_source`
- `sink` (Optional) - Custom output sink for results
- `sink_connection_point` (str) - Where to attach the sink in the pipeline:
  - `"detector"` - After face detection (default)
  - `"recognizer"` - After face recognition and embedding extraction

**Returns:**
- `Composition` - Pipeline composition object (call `.wait()` to run)
- `Watchdog` - Monitoring object for pipeline health

#### Example 1: Basic Security Monitoring

Monitor webcam and alert on unknown faces:

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    video_source=0,  # Webcam
    db_path="./security_db.lance",
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    live_stream_mode="LOCAL",
)

tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()
composition.wait()
```

#### Example 2: RTSP Camera with Clip Recording

Monitor RTSP camera, save clips, and send notifications:

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceTrackerConfig(
    video_source="rtsp://192.168.1.100/stream",
    db_path="./security_db.lance",
    
    # Alerting
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    alert_once=True,
    clip_duration=150,  # 5 seconds at 30 FPS
    
    # Clip storage
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    ),
    
    # Notifications
    notification_config="mailto://security@company.com",
    notification_message="⚠️ Unknown person at ${time}",
    
    # Live streaming
    live_stream_mode="WEB",
    live_stream_rtsp_url="entrance_camera",
)

tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline()
composition.wait()
```

#### Example 3: Custom Frame Source

Use custom frame generator instead of `video_source`:

```python
import degirum_face
import cv2

def my_frame_generator():
    cap = cv2.VideoCapture("custom_source.mp4")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()

config = degirum_face.FaceTrackerConfig(
    db_path="./db.lance",
    live_stream_mode="LOCAL",
)

tracker = degirum_face.FaceTracker(config)
composition, watchdog = tracker.start_face_tracking_pipeline(
    frame_iterator=my_frame_generator()
)
composition.wait()
```

#### What Happens in the Pipeline

The tracking pipeline performs these steps for each frame:

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

### predict_batch()

**Purpose:** Process video streams and return inference results for each frame with programmatic access to recognition data.

**When to use:**
- Need access to raw results for custom processing
- Logging face detections to database
- Integration with other analytics systems
- Building custom alerting logic
- No need for built-in alerting/clip features

**Why not use `start_face_tracking_pipeline()`?**
- `start_face_tracking_pipeline()` is designed for production monitoring with alerts/clips
- `predict_batch()` gives you direct access to results for custom workflows

**Signature:**
```python
predict_batch(stream: Iterable) -> Iterator[dg.postprocessor.InferenceResults]
```

**Parameters:**
- `stream` - Iterator yielding video frames as numpy arrays

**Returns:**
- Iterator of `InferenceResults` objects with face detection and recognition data. Each result contains:
  - `"face_embeddings"` - Face embedding vector
  - `"face_db_id"` - Database ID of recognized face
  - `"face_attributes"` - Recognized face attributes (e.g., person name)
  - `"face_similarity_score"` - Similarity score from database search
  - `"frame_id"` - Input frame ID
  - `faces` property - List of `FaceRecognitionResult` objects

#### Example: Custom Logging System

Process video and log all face detections:

```python
import degirum_face
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

config = degirum_face.FaceTrackerConfig(
    db_path="./face_db.lance",
)

tracker = degirum_face.FaceTracker(config)

# Process and log results
log_file = open("face_detections.jsonl", "w")

for result in tracker.predict_batch(frame_generator()):
    timestamp = datetime.now().isoformat()
    
    for face in result.faces:
        log_entry = {
            "timestamp": timestamp,
            "track_id": face.track_id,
            "attributes": face.attributes,
            "similarity": face.similarity_score,
            "bbox": face.bbox
        }
        log_file.write(json.dumps(log_entry) + "\n")
    
    print(f"Frame: {result._frame_info}, Faces: {len(result.faces)}")

log_file.close()
```

#### Example: Custom Alert Logic

Implement custom alerting based on multiple conditions:

```python
import degirum_face
import cv2

def frame_generator():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()

config = degirum_face.FaceTrackerConfig(
    db_path="./vip_database.lance",
)

tracker = degirum_face.FaceTracker(config)

known_track_ids = set()

for result in tracker.predict_batch(frame_generator()):
    for face in result.faces:
        # Custom logic: Alert only for VIPs not seen before
        if face.attributes and face.attributes.startswith("VIP_"):
            if face.track_id not in known_track_ids:
                print(f"🎯 VIP detected: {face.attributes}")
                known_track_ids.add(face.track_id)
                # Send custom notification...
```

---

### find_faces_in_file()

**Purpose:** Analyze a local video file to find and track all faces, optionally creating an annotated output video.

**When to use:**
- Post-incident review of recorded footage
- Extract faces from video for database enrollment
- Analyze security camera recordings
- Create annotated videos for review
- Build face databases from surveillance footage

**Signature:**
```python
find_faces_in_file(
    file_path: str,
    save_annotated: bool = True,
    output_video_path: Optional[str] = None,
    compute_clusters: bool = True
) -> Dict[int, FaceAttributes]
```

**Parameters:**
- `file_path` (str) - Path to the input video file
- `save_annotated` (bool) - Whether to save an annotated video (default: True)
- `output_video_path` (Optional[str]) - Path for the annotated output video
- `compute_clusters` (bool) - Whether to compute K-means clustering on embeddings (default: True)

**Returns:**
- `Dict[int, FaceAttributes]` - Dictionary mapping track IDs to face data:
  - Each `FaceAttributes` object contains embeddings and attributes (if recognized)
  - Track IDs are persistent across frames
  - Embeddings are clustered if `compute_clusters=True`

#### Example 1: Review Footage and Enroll Unknowns

Analyze video, review faces, and enroll new people:

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    db_path="./employee_db.lance",
)

tracker = degirum_face.FaceTracker(config)

# Analyze video
faces = tracker.find_faces_in_file(
    file_path="lobby_camera_2026-01-02.mp4",
    save_annotated=True,
    output_video_path="lobby_annotated.mp4"
)

print(f"Found {len(faces)} unique individuals")

# Review and enroll unknown faces
for track_id, face_data in faces.items():
    if face_data.attributes is None:  # Unknown person
        print(f"\nTrack {track_id}:")
        print(f"  Appearances: {len(face_data.embeddings)} frames")
        
        # Prompt for identity
        name = input("  Who is this? (press Enter to skip): ")
        
        if name:
            face_data.attributes = name
            tracker.enroll(face_data)
            print(f"  ✅ Enrolled as {name}")
```

#### Example 2: Extract All Faces for Review

Get all faces without enrolling:

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    db_path="./face_db.lance",
)

tracker = degirum_face.FaceTracker(config)

faces = tracker.find_faces_in_file(
    file_path="incident_video.mp4",
    save_annotated=True,
    output_video_path="incident_annotated.mp4"
)

# Print report
print("Face Detection Report")
print("=" * 50)
for track_id, face_data in faces.items():
    status = "KNOWN" if face_data.attributes else "UNKNOWN"
    name = face_data.attributes or "???"
    print(f"Track {track_id:3d}: {status:8s} {name:20s} ({len(face_data.embeddings):3d} samples)")
```

#### Example 3: Bulk Enrollment from Training Videos

Create enrollment videos for each person and bulk enroll:

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    db_path="./company_db.lance",
)

tracker = degirum_face.FaceTracker(config)

# Process enrollment video for each employee
enrollment_videos = {
    "Alice Smith": "enrollments/alice.mp4",
    "Bob Johnson": "enrollments/bob.mp4",
    "Carol Davis": "enrollments/carol.mp4",
}

for name, video_path in enrollment_videos.items():
    print(f"Processing {name}...")
    
    faces = tracker.find_faces_in_file(
        file_path=video_path,
        save_annotated=False,
        compute_clusters=True
    )
    
    # Take the most prominent face (most samples)
    if faces:
        main_face = max(faces.values(), key=lambda f: len(f.embeddings))
        main_face.attributes = name
        tracker.enroll(main_face)
        print(f"  ✅ Enrolled {name} with {len(main_face.embeddings)} samples")
```

---

### find_faces_in_clip()

**Purpose:** Analyze a video clip from object storage (S3 or local), similar to `find_faces_in_file()` but for cloud/storage-based clips.

**When to use:**
- Review alert clips saved by `start_face_tracking_pipeline()`
- Batch processing of clips from S3 storage
- Post-process stored surveillance footage
- Centralized clip analysis from multiple cameras

**Why not use `find_faces_in_file()`?**
- `find_faces_in_file()` requires local files
- `find_faces_in_clip()` handles download/upload from object storage automatically

**Signature:**
```python
find_faces_in_clip(
    clip_object_name: str,
    save_annotated: bool = True,
    compute_clusters: bool = True
) -> Dict[int, FaceAttributes]
```

**Parameters:**
- `clip_object_name` (str) - Name of the video clip in object storage
- `save_annotated` (bool) - Whether to save annotated video back to storage (default: True)
- `compute_clusters` (bool) - Whether to compute K-means clustering on embeddings (default: True)

**Returns:**
- `Dict[int, FaceAttributes]` - Dictionary mapping track IDs to face data (same as `find_faces_in_file()`)

**Requirements:**
- `clip_storage_config` must be configured in `FaceTrackerConfig`

#### Example 1: Review Alert Clips from S3

Process all unknown person clips from cloud storage:

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceTrackerConfig(
    db_path="./security_db.lance",
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="s3.amazonaws.com",
        access_key="YOUR_KEY",
        secret_key="YOUR_SECRET",
        bucket="security-clips"
    )
)

tracker = degirum_face.FaceTracker(config)

# List all clips
clip_manager = degirum_face.FaceClipManager(config.clip_storage_config)
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
    
    # Review unknown faces
    for track_id, face_data in faces.items():
        if face_data.attributes is None:
            print(f"    Track {track_id}: UNKNOWN ({len(face_data.embeddings)} samples)")
```

**Note:** The annotated video is saved with `_annotated` suffix (e.g., `clip_annotated.mp4`) in the same storage location.

#### Example 2: Enroll from Cloud Clips

Review clips and enroll identified faces:

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceTrackerConfig(
    db_path="./face_db.lance",
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./local_clips",
        bucket="unknown_alerts"
    )
)

tracker = degirum_face.FaceTracker(config)
clip_manager = degirum_face.FaceClipManager(config.clip_storage_config)

for clip_name in clip_manager.list_clips().keys():
    faces = tracker.find_faces_in_clip(clip_name)
    
    print(f"\nClip: {clip_name}")
    for track_id, face_data in faces.items():
        if face_data.attributes is None:
            name = input(f"  Track {track_id} - Who is this? (Enter to skip): ")
            if name:
                face_data.attributes = name
                tracker.enroll(face_data)
                print(f"    ✅ Enrolled as {name}")
```

---

### enroll()

**Purpose:** Enroll face(s) into the database using embeddings extracted from video analysis.

**When to use:**
- After analyzing video with `find_faces_in_file()` or `find_faces_in_clip()`
- Building face databases from surveillance footage
- Enrollment with multiple face samples (better accuracy than single images)

**Why not use `FaceRecognizer.enroll_batch()`?**
- `FaceRecognizer.enroll_batch()` processes individual images
- `FaceTracker.enroll()` uses clustered embeddings from video (multiple angles/expressions)
- Video-based enrollment provides more robust face representations

**Signature:**
```python
enroll(face_list: Union[FaceAttributes, List[FaceAttributes]])
```

**Parameters:**
- `face_list` - Single `FaceAttributes` object or list of objects to enroll
  - Must have `attributes` property set (e.g., person name)
  - Must contain `embeddings` (populated by `find_faces_in_file()` or `find_faces_in_clip()`)

#### Workflow

1. Run `find_faces_in_file()` or `find_faces_in_clip()` to extract faces
2. Assign `attributes` (person name) to each face you want to enroll
3. Call `enroll()` with the face data

#### Example 1: Enroll Single Person

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    db_path="./face_db.lance",
)

tracker = degirum_face.FaceTracker(config)

# Extract faces from enrollment video
faces = tracker.find_faces_in_file(
    "enrollment_john.mp4",
    save_annotated=False
)

# Enroll the main face
main_face = list(faces.values())[0]
main_face.attributes = "John Smith"
tracker.enroll(main_face)

print(f"Enrolled John Smith with {len(main_face.embeddings)} samples")
```

#### Example 2: Enroll Multiple People

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    db_path="./employee_db.lance",
)

tracker = degirum_face.FaceTracker(config)

# Process video with multiple people
faces = tracker.find_faces_in_file("team_meeting.mp4")

# Assign identities
face_list = list(faces.values())
face_list[0].attributes = "Alice Jones"
face_list[1].attributes = "Bob Wilson"
face_list[2].attributes = "Carol Brown"

# Enroll all at once
tracker.enroll(face_list)

print(f"Enrolled {len(face_list)} people")
```

#### Example 3: Interactive Enrollment

```python
import degirum_face

config = degirum_face.FaceTrackerConfig(
    db_path="./face_db.lance",
)

tracker = degirum_face.FaceTracker(config)

faces = tracker.find_faces_in_file("footage.mp4")

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

---

## Workflow Patterns

### Pattern 1: Live Monitoring → Review Clips → Enroll

**Scenario:** Security system that records unknown persons, then allows review and enrollment

```python
import degirum_face
import degirum_tools

# Step 1: Live monitoring (run continuously)
config = degirum_face.FaceTrackerConfig(
    db_path="./security_db.lance",
    video_source="rtsp://camera/stream",
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./clips",
        bucket="unknowns"
    ),
    clip_duration=150,
)

tracker = degirum_face.FaceTracker(config)
# composition, watchdog = tracker.start_face_tracking_pipeline()
# composition.wait()

# Step 2: Review clips later (run periodically)
clip_manager = degirum_face.FaceClipManager(config.clip_storage_config)
for clip_name in clip_manager.list_clips().keys():
    faces = tracker.find_faces_in_clip(clip_name)
    
    for track_id, face_data in faces.items():
        name = input(f"Who is track {track_id}? ")
        if name:
            face_data.attributes = name
            tracker.enroll(face_data)
```

### Pattern 2: Batch Processing → Enrollment

**Scenario:** Build database from historical footage

```python
import degirum_face
import os

config = degirum_face.FaceTrackerConfig(
    db_path="./historical_db.lance",
)

tracker = degirum_face.FaceTracker(config)

# Process all videos in directory
video_dir = "./historical_footage"
for video_file in os.listdir(video_dir):
    if video_file.endswith(".mp4"):
        print(f"Processing: {video_file}")
        
        faces = tracker.find_faces_in_file(
            os.path.join(video_dir, video_file),
            save_annotated=True
        )
        
        # Interactive enrollment
        for track_id, face_data in faces.items():
            if not face_data.attributes:
                name = input(f"  Track {track_id}: ")
                if name:
                    face_data.attributes = name
                    tracker.enroll(face_data)
```

### Pattern 3: Custom Analytics Pipeline

**Scenario:** Integrate face tracking with custom analytics

```python
import degirum_face
import cv2
import pandas as pd

def frame_generator():
    cap = cv2.VideoCapture("analytics.mp4")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()

config = degirum_face.FaceTrackerConfig(
    db_path="./analytics_db.lance",
)

tracker = degirum_face.FaceTracker(config)

# Collect data
records = []
for result in tracker.predict_batch(frame_generator()):
    for face in result.faces:
        records.append({
            "timestamp": result._frame_info,
            "person": face.attributes or "Unknown",
            "confidence": face.similarity_score,
            "bbox_area": (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1])
        })

# Analyze with pandas
df = pd.DataFrame(records)
print(df.groupby("person").size())
print(df.groupby("person")["confidence"].mean())
```

---

**Related Documentation:**
- [Quick Start Guide](face_tracker_quickstart.md) - Get started quickly with simple examples
- [Configuration Reference](face_tracker_config.md) - Detailed configuration options
- **[FaceRecognizer Guide](face_recognizer.md)** - Batch image processing without tracking
