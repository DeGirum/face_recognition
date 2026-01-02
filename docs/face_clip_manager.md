# FaceClipManager Guide

**Use FaceClipManager to analyze faces in pre-recorded video clips stored in object storage.**

---

## Overview

`FaceClipManager` is designed for **post-processing video clips** to identify and analyze faces. Unlike `FaceTracker` which processes live video streams in real-time, `FaceClipManager` works with video files already stored in S3-compatible object storage.

**Real-world scenarios:**

- **Security footage analysis** - Review recorded surveillance clips for specific individuals
- **Post-event processing** - Analyze recorded conference or event videos for attendee identification
- **Batch video analysis** - Process archived video content to build face databases
- **Clip annotation** - Generate annotated versions of video clips with face identifications
- **Forensic analysis** - Detailed frame-by-frame face analysis of recorded incidents

---

## Prerequisites

Before using FaceClipManager:

1. **Object storage configured** - S3-compatible storage (AWS S3, MinIO, etc.) with access credentials
2. **Video clips uploaded** - MP4 video files stored in your object storage bucket
3. **Face database** - Lance database with known face embeddings (can be empty for clustering)
4. **AI models available** - Face detection and embedding models accessible

---

## FaceClipManager vs FaceTracker

| Use Case | Class | Key Difference |
|----------|-------|----------------|
| Live video streams | `FaceTracker` | Real-time processing with persistent track IDs |
| Pre-recorded clips | `FaceClipManager` | Batch processing of stored video files |
| Security monitoring | `FaceTracker` | Continuous streaming with alerts |
| Forensic analysis | `FaceClipManager` | Detailed post-processing with annotation |
| Archive processing | `FaceClipManager` | Batch analysis of historical footage |

**Key insight:** `FaceClipManager` is for analyzing what already happened; `FaceTracker` is for monitoring what's happening now.

---

## Table of Contents
- [Python Configuration Example](#python-configuration-example)
- [YAML Configuration Structure](#yaml-configuration-structure)
- [FaceClipManager Methods](#faceclipmanager-methods)
- [Complete Examples](#complete-examples)

---

## Python Configuration Example

`FaceClipManagerConfig` extends `FaceRecognizerConfig` and requires object storage configuration:

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceClipManagerConfig(
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
    db_path="./face_analysis_db.lance",
    cosine_similarity_threshold=0.6,
    
    # Face filters
    face_filters=degirum_face.FaceFilterConfig(
        enable_small_face_filter=True,
        min_face_size=50,
        enable_frontal_filter=True,
        enable_reid_expiration_filter=True,  # Always enabled (forces every frame)
        reid_expiration_frames=1  # Always 1 for clip analysis
    ),
    
    # Clip storage configuration (REQUIRED)
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="s3.amazonaws.com",
        access_key="YOUR_ACCESS_KEY",
        secret_key="YOUR_SECRET_KEY",
        bucket="security-footage",
        url_expiration_s=3600
    ),
)

clip_manager = degirum_face.FaceClipManager(config)
```

**Note:** For FaceClipManager, `reid_expiration_filter` is automatically enabled with `reid_expiration_frames=1` to ensure every frame is analyzed.

---

## YAML Configuration Structure

Complete YAML structure for FaceClipManager:

```yaml
# Complete FaceClipManager YAML Configuration

# Face detection model
face_detector:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"
  model_zoo_url: degirum/hailo

# Face embedding model
face_embedder:
  hardware: HAILORT/HAILO8
  inference_host_address: "@cloud"
  model_zoo_url: degirum/hailo

# Database settings
db_path: ./face_analysis_db.lance
cosine_similarity_threshold: 0.6

# Face filters
face_filters:
  enable_small_face_filter: true
  min_face_size: 50
  enable_zone_filter: false
  zone: []
  enable_frontal_filter: true
  enable_shift_filter: false
  enable_reid_expiration_filter: true
  reid_expiration_frames: 1

# Clip storage configuration (REQUIRED)
storage:
  endpoint: s3.amazonaws.com
  access_key: YOUR_ACCESS_KEY
  secret_key: YOUR_SECRET_KEY
  bucket: security-footage
  url_expiration_s: 3600
```

**Loading from YAML:**

```python
import degirum_face

config, _ = degirum_face.FaceClipManagerConfig.from_yaml(yaml_file="clip_analysis.yaml")
clip_manager = degirum_face.FaceClipManager(config)
```

---

## FaceClipManager Methods

### find_faces_in_clip()

Analyzes a video clip stored in object storage.

**Signature:**
```python
def find_faces_in_clip(
    clip_object_name: str,
    *,
    save_annotated: bool = True,
    compute_clusters: bool = True
) -> ObjectMap
```

**Parameters:**
- **`clip_object_name`** - Name of video clip in object storage (e.g., `"2024/incident_01.mp4"`)
- **`save_annotated`** - If `True`, saves annotated video with face labels back to storage
- **`compute_clusters`** - If `True`, performs K-means clustering on embeddings to group similar faces

**Returns:** `ObjectMap` containing face IDs and their associated embeddings table

**Example:**
```python
# Analyze a stored clip
face_map = clip_manager.find_faces_in_clip(
    clip_object_name="security/lobby_2024_12_23.mp4",
    save_annotated=True,
    compute_clusters=True
)

# Access results
for face_id, face_data in face_map.map.items():
    print(f"Face ID: {face_id}")
    print(f"Name: {face_data.name}")
    print(f"Embeddings count: {len(face_data.embeddings)}")
```

**What happens:**
1. Downloads video clip from object storage to temporary location
2. Runs face detection and embedding on every frame
3. Matches faces against database
4. Performs K-means clustering (if enabled)
5. Saves annotated video as `<original_name>_annotated.mp4` (if enabled)
6. Returns face map with all detected faces and embeddings

---

### find_faces_in_file()

Analyzes a local video file (not in object storage).

**Signature:**
```python
def find_faces_in_file(
    file_path: str,
    *,
    save_annotated: bool = True,
    output_video_path: Optional[str] = None,
    compute_clusters: bool = True
) -> ObjectMap
```

**Parameters:**
- **`file_path`** - Path to local video file
- **`save_annotated`** - If `True`, saves annotated video to file
- **`output_video_path`** - Path for annotated video (defaults to `<original>_annotated.mp4`)
- **`compute_clusters`** - If `True`, performs K-means clustering on embeddings

**Returns:** `ObjectMap` containing face IDs and embeddings

**Example:**
```python
# Analyze a local video file
face_map = clip_manager.find_faces_in_file(
    file_path="./downloads/meeting_recording.mp4",
    save_annotated=True,
    output_video_path="./downloads/meeting_annotated.mp4",
    compute_clusters=True
)

# Access clustered embeddings
for face_id, face_data in face_map.map.items():
    print(f"Face: {face_data.name}, Clusters: {len(face_data.embeddings)}")
```

---

### list_clips()

Lists all video clips in object storage bucket.

**Signature:**
```python
def list_clips() -> Dict[str, dict]
```

**Returns:** Dictionary mapping clip base names to file objects:
- `"original"` - Original video clip
- `"annotated"` - Annotated video (if exists)
- `"json"` - JSON annotations (if exists)

**Example:**
```python
clips = clip_manager.list_clips()

for clip_name, files in clips.items():
    print(f"Clip: {clip_name}")
    if "original" in files:
        print(f"  Original: {files['original'].object_name}")
    if "annotated" in files:
        print(f"  Annotated: {files['annotated'].object_name}")
    if "json" in files:
        print(f"  Annotations: {files['json'].object_name}")
```

---

### download_clip()

Downloads a video clip from object storage.

**Signature:**
```python
def download_clip(filename: str) -> bytes
```

**Parameters:**
- **`filename`** - Name of clip to download (with or without `.mp4` extension)

**Returns:** Bytes of the video file

**Example:**
```python
# Download a clip
video_bytes = clip_manager.download_clip("security/incident_01.mp4")

# Save locally
with open("local_copy.mp4", "wb") as f:
    f.write(video_bytes)
```

---

### remove_clip()

Removes a video clip from object storage.

**Signature:**
```python
def remove_clip(filename: str)
```

**Parameters:**
- **`filename`** - Name of clip to remove

**Example:**
```python
# Remove a single clip
clip_manager.remove_clip("security/old_footage.mp4")
```

---

### remove_all_clips()

Removes all video clips from object storage.

**Signature:**
```python
def remove_all_clips()
```

**Example:**
```python
# Clear all clips (use with caution!)
clip_manager.remove_all_clips()
```

---

## Complete Examples

### Example 1: Forensic Analysis of Security Incident

```python
import degirum_face
import degirum_tools

# Configure for detailed analysis
config = degirum_face.FaceClipManagerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="HAILORT/HAILO8",
        inference_host_address="@cloud"
    ),
    db_path="./security_personnel.lance",
    cosine_similarity_threshold=0.6,
    face_filters=degirum_face.FaceFilterConfig(
        enable_small_face_filter=True,
        min_face_size=40,
        enable_frontal_filter=False,  # Capture all angles
    ),
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="s3.amazonaws.com",
        access_key="YOUR_ACCESS_KEY",
        secret_key="YOUR_SECRET_KEY",
        bucket="security-incidents"
    ),
)

clip_manager = degirum_face.FaceClipManager(config)

# List all available clips
clips = clip_manager.list_clips()
print(f"Found {len(clips)} clips in storage")

# Analyze specific incident
incident_clip = "2024/december/lobby_incident_20241223.mp4"
print(f"Analyzing {incident_clip}...")

face_map = clip_manager.find_faces_in_clip(
    clip_object_name=incident_clip,
    save_annotated=True,
    compute_clusters=True
)

# Report findings
print(f"\nAnalysis Results:")
print(f"Total unique faces detected: {len(face_map.map)}")

for face_id, face_data in face_map.map.items():
    status = "KNOWN" if face_data.name != "Unknown" else "UNKNOWN"
    print(f"  Face ID {face_id}: {face_data.name} ({status})")
    print(f"    Appearances: {len(face_data.embeddings)} frame clusters")
    print(f"    Confidence: {face_data.distance:.3f}")
```

### Example 2: Batch Processing Archive

```python
import degirum_face
import degirum_tools

config = degirum_face.FaceClipManagerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="ONNX/CPU",
        inference_host_address="@local"
    ),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec(
        device_type="ONNX/CPU",
        inference_host_address="@local"
    ),
    db_path="./archive_analysis.lance",
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="minio.local:9000",
        access_key="admin",
        secret_key="password",
        bucket="video-archive"
    ),
)

clip_manager = degirum_face.FaceClipManager(config)

# Process all clips in archive
all_clips = clip_manager.list_clips()
results = {}

for clip_name in all_clips.keys():
    print(f"Processing {clip_name}...")
    
    try:
        face_map = clip_manager.find_faces_in_clip(
            clip_object_name=clip_name + ".mp4",
            save_annotated=True,
            compute_clusters=True
        )
        
        results[clip_name] = {
            "faces_found": len(face_map.map),
            "status": "completed"
        }
    except Exception as e:
        results[clip_name] = {
            "status": "failed",
            "error": str(e)
        }

# Summary report
print(f"\nBatch Processing Summary:")
print(f"Total clips processed: {len(results)}")
print(f"Successful: {sum(1 for r in results.values() if r['status'] == 'completed')}")
print(f"Failed: {sum(1 for r in results.values() if r['status'] == 'failed')}")
print(f"Total faces found: {sum(r.get('faces_found', 0) for r in results.values())}")
```

### Example 3: Local File Analysis Without Object Storage

```python
import degirum_face
import degirum_tools

# Note: Still need storage config for FaceClipManager initialization,
# but find_faces_in_file() works with local files
config = degirum_face.FaceClipManagerConfig(
    db_path="./local_analysis.lance",
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="dummy",  # Required but not used for local file analysis
        bucket="dummy"
    ),
)

clip_manager = degirum_face.FaceClipManager(config)

# Analyze local video file
face_map = clip_manager.find_faces_in_file(
    file_path="./meeting_recording.mp4",
    save_annotated=True,
    output_video_path="./meeting_annotated.mp4",
    compute_clusters=True
)

print(f"Found {len(face_map.map)} unique faces in recording")
```

---

## Next Steps

- For real-time video tracking, see [FaceTracker Guide](face_tracker.md)
- For single image/batch processing, see [FaceRecognizer Guide](face_recognizer.md)
- For configuration details, see [Configuration Guide](GUIDE.md)
