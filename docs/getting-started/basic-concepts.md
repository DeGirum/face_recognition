# Basic Concepts

Understanding these core concepts will help you work effectively with `degirum-face`.

## Face Recognition vs. Face Tracking

`degirum-face` provides two main approaches:

| | **FaceRecognizer** | **FaceTracker** |
|---|---|---|
| **Use Case** | Static images or batches | Video streams or files |
| **Temporal Awareness** | None (each image is independent) | Tracks faces across frames |
| **Real-Time Events** | No | Yes (alerts, streaming) |
| **Primary Methods** | `predict()`, `predict_batch()`, `enroll_image()` | `start_face_tracking_pipeline()`, `find_faces_in_file()` |
| **Best For** | Photo albums, batch processing, simple recognition | Surveillance, video analysis, NVR systems |

**When to use FaceRecognizer:**
- Processing photos or image collections
- One-time batch recognition
- Building a face database from images
- Simple recognize-and-done workflows

**When to use FaceTracker:**
- Live camera feeds or video files
- Tracking the same person across frames
- Real-time alerts on face confirmation
- Clip extraction for detected faces
- Video surveillance applications

## Face Recognition Pipeline

Every face recognition operation goes through these stages:

```
┌─────────────┐     ┌──────────┐     ┌───────────┐     ┌──────────────┐
│ Input Image │ ──> │  Detect  │ ──> │   Align   │ ──> │   Embedding  │
│             │     │  Faces   │     │ & Extract │     │  Extraction  │
└─────────────┘     └──────────┘     └───────────┘     └──────────────┘
                                                                │
                                                                v
                                                        ┌──────────────┐
                                                        │   Database   │
                                                        │   Search &   │
                                                        │    Match     │
                                                        └──────────────┘
```

### 1. Face Detection
Locates faces in the image and returns bounding boxes.

**Model:** YOLOv8-based detector  
**Output:** Bounding box coordinates (x, y, width, height)

### 2. Landmark Detection & Alignment
Finds facial keypoints (eyes, nose, mouth) and aligns the face to a standard pose.

**Model:** MobileFaceNet-based landmark detector  
**Output:** 5 facial landmarks, aligned 112×112 face crop

### 3. Embedding Extraction
Converts the aligned face into a numerical vector (embedding) that captures facial features.

**Model:** ArcFace ResNet100  
**Output:** 512-dimensional embedding vector

### 4. Database Search & Matching
Compares the embedding against enrolled faces using cosine similarity.

**Database:** LanceDB (vector database)  
**Output:** Identity + confidence score

## Key Configuration Parameters

### Similarity Threshold

Controls how strict matching is:

```python
config = degirum_face.FaceRecognizerConfig(
    similarity_threshold=0.50  # Default: 50% similarity required
)
```

- **Higher threshold (0.60-0.80):** Stricter matching, fewer false positives
- **Lower threshold (0.30-0.50):** More lenient matching, may accept similar-looking people
- **Recommended:** Start with 0.50, adjust based on your accuracy needs

### Face Database Path

Where enrolled faces are stored:

```python
config = degirum_face.FaceRecognizerConfig(
    face_database_path="./my_faces.lance"
)
```

The database is a LanceDB vector store containing:
- Face embeddings (512-D vectors)
- Person identities (names/IDs)
- Metadata (enrollment timestamps, etc.)

### Model Selection

Choose models based on your hardware:

```python
config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec(
        device_type="HAILORT/HAILO8",  # Your hardware accelerator
        inference_host_address="@local"  # Or "@cloud" for cloud inference
    )
)
```

See [Hardware & Deployment](../guides/face-recognizer/deployment.md) for device types.

## Face Records

All face results are returned as `FaceRecognitionResult` objects:

```python
result = face_recognizer.predict("photo.jpg")

for face in result.faces:
    print(f"Person: {face.attributes}")             # Person's name or None
    print(f"Confidence: {face.similarity_score}")   # Similarity score (0.0-1.0)
    print(f"Bounding Box: {face.bbox}")             # [x1, y1, x2, y2]
    print(f"Embedding: {face.embeddings}")          # 512-D vector
    print(f"Database ID: {face.db_id}")             # DB ID if matched
    print(f"Detection: {face.detection_score}")     # Detection confidence
```

### Identity Assignment

- **Known face:** `attributes` contains the enrolled person's name
- **Unknown face:** `attributes` is `None`
- **Confidence:** Higher `similarity_score` = more similar to enrolled face (max 1.0)

## Face Tracking Concepts

### Confirmation Types

FaceTracker uses confirmation logic to reduce false alarms:

```yaml
confirmation_type: "consecutive"  # or "cumulative"
confirmation_frames: 3
```

- **consecutive:** Face must appear in N frames in a row
- **cumulative:** Face must appear in N total frames (can be non-consecutive)

### Alerting

Trigger actions when a face is confirmed:

```yaml
alerting_enabled: true
alerting_mode: "all"  # Alert for every person
```

Alerts are sent via callback function:

```python
def my_alert_callback(alert_data):
    print(f"Alert: {alert_data['identity']} detected!")
    # Send notification, save to database, etc.

config.alerting_callback = my_alert_callback
```

### Clip Storage

Save video clips when faces are detected:

```yaml
clip_storage_enabled: true  # Requires alerting_enabled: true
clip_storage_output_folder: "./face_clips"
clip_storage_duration_seconds: 5
```

Each clip contains:
- Video segment around the face confirmation
- Face thumbnail
- Metadata (identity, timestamp, confidence)

## Model Inference Modes

### Local Inference (`@local`)

Models run on your local hardware:

```python
inference_host_address="@local"
```

- **Pros:** Low latency, no internet needed, full privacy
- **Cons:** Requires compatible hardware accelerator

### Cloud Inference (`@cloud`)

Models run on DeGirum cloud servers:

```python
inference_host_address="@cloud"
```

- **Pros:** No local hardware needed, try any accelerator type
- **Cons:** Requires internet, higher latency, data leaves your system

### Hybrid (IP Address)

Run models on a separate inference server:

```python
inference_host_address="192.168.1.100"
```

- **Pros:** Offload compute to dedicated server, share accelerators
- **Cons:** Requires network infrastructure

## Common Patterns

### Enroll Multiple Photos of Same Person

```python
face_recognizer.enroll_image("alice_1.jpg", "Alice")
face_recognizer.enroll_image("alice_2.jpg", "Alice")
face_recognizer.enroll_image("alice_3.jpg", "Alice")
```

Multiple enrollments improve recognition accuracy across different poses/lighting.

### Unknown Face Handling

```python
result = face_recognizer.predict("photo.jpg")

for face in result.faces:
    if face.attributes == "Unknown":
        if face.similarity_score and face.similarity_score < 0.3:
            print("Very low similarity - likely a new person")
        elif face.similarity_score:
            print(f"Close match to enrolled face: {face.similarity_score}")
```

Low confidence on unknown faces means the face is similar to someone enrolled but below threshold.

### Database Management

```python
# List all enrolled identities
identities = face_recognizer.list_identities()

# Remove a person from database
face_recognizer.delete_identity("Bob")

# Clear entire database
face_recognizer.clear_database()
```

## Next Steps

- **[Face Recognizer Overview](../guides/face-recognizer/overview.md)** - Deep dive into image recognition
- **[Face Tracker Quick Start](../guides/face-tracker/quickstart.md)** - Start tracking video
- **[Configuration Guide](../guides/face-recognizer/configuration.md)** - Customize your setup
