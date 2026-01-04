# Face Data Classes Reference

## Overview

Face data in `degirum-face` is represented by two related classes:

- **`FaceAttributes`** - Contains face identity data (embeddings, attributes, images)
- **`FaceRecognitionResult`** - Includes all `FaceAttributes` properties plus detection metadata (bounding box, scores, landmarks)

## FaceAttributes

Contains face identity data without detection-specific information. Used primarily for enrollment workflows.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `attributes` | str or None | Person name or metadata |
| `db_id` | str or None | Database ID if stored |
| `embeddings` | list | Face embedding vector(s) (512-D each). May contain multiple embeddings when returned by `find_faces_in_file()` / `find_faces_in_clip()` |
| `images` | list | Cropped face images (numpy arrays) corresponding to embeddings. May contain multiple images when returned by `find_faces_in_file()` / `find_faces_in_clip()` |

### When It's Used

`find_faces_in_file()` and `find_faces_in_clip()` return `Dict[int, FaceAttributes]` - a mapping of track IDs to face data. Each `FaceAttributes` object contains:
- **Multiple embeddings** - One for each frame where the face was detected (or sampled based on reid_expiration_frames)
- **Multiple images** - Corresponding cropped face images for each embedding
- This accumulated data across frames provides robust face representations for enrollment

Also used as input to `FaceTracker.enroll()` for batch enrollment.

### Usage Example

```python
# Analyze video to extract faces
faces = tracker.find_faces_in_file("video.mp4")

# faces is Dict[int, FaceAttributes] - maps track_id to face data
for track_id, face_data in faces.items():
    print(f"Track {track_id}:")
    print(f"  Person: {face_data.attributes}")
    print(f"  Embeddings: {len(face_data.embeddings)}")  # Multiple per track
    print(f"  Images: {len(face_data.images)}")  # Multiple per track
    
    # Enroll if unknown
    if not face_data.attributes:
        tracker.enroll(face_data)
```

## FaceRecognitionResult

Includes all `FaceAttributes` properties plus detection-specific metadata. Used for real-time recognition results.

### Properties

All `FaceAttributes` properties (`attributes`, `db_id`, `embeddings`, `images`) plus:

| Property | Type | Description |
|----------|------|-------------|
| `bbox` | list | Bounding box `[x1, y1, x2, y2]` |
| `detection_score` | float | Face detection confidence 0.0-1.0 |
| `similarity_score` | float or None | Match confidence 0.0-1.0 (None if unknown) |
| `landmarks` | array | Facial keypoints (eyes, nose, mouth) |
| `frame_id` | int or None | Frame number (when applicable) |

**Important notes:**
- The `embeddings` and `images` lists contain a **single item** when returned by `enroll_image()`, `enroll_batch()`, `predict()`, or `predict_batch()`. Access using `result.embeddings[0]` and `result.images[0]`. This is different from `find_faces_in_file()` / `find_faces_in_clip()` which return multiple embeddings/images per track.
- When using FaceTracker, `track_id` is in `InferenceResults.results`, not as a property. Access via `result.results[i].get("track_id")`

### When It's Used

- Returned by `enroll_image()` and `enroll_batch()`
- Contained in `InferenceResults.faces` from `predict()` and `predict_batch()`

### Usage Examples

**Check if face was detected:**

```python
result = recognizer.enroll_image("photo.jpg", "Alice")
if result:
    print(f"Enrolled: {result.attributes}")
else:
    print("No face detected")
```

**Access detection properties:**

```python
result = recognizer.predict("photo.jpg")

for face in result.faces:
    if face.attributes:
        print(f"Known: {face.attributes} (confidence: {face.similarity_score:.2f})")
    else:
        print(f"Unknown person (detection score: {face.detection_score:.2f})")
    
    # Access bounding box
    x1, y1, x2, y2 = face.bbox
    print(f"Face location: ({x1}, {y1}) to ({x2}, {y2})")
```

**Access embeddings and cropped images:**

```python
result = recognizer.enroll_image("photo.jpg", "Alice")
embedding_vector = result.embeddings[0]  # 512-D numpy array
cropped_face = result.images[0]  # Aligned 112×112 face image

print(f"Embedding shape: {embedding_vector.shape}")  # (512,)
cv2.imwrite("cropped_face.jpg", cropped_face)
```

**FaceTracker - Access tracking data:**

```python
for result in tracker.predict_batch(video_source):
    # result.faces and result.results correspond at the same index
    for i in range(len(result.faces)):
        track_id = result.results[i].get("track_id")
        person = result.faces[i].attributes
        print(f"Track {track_id}: {person}")
```

## Return Types by Method

### FaceRecognizer

| Method | Return Type |
|--------|-------------|
| `enroll_image()` | `Optional[FaceRecognitionResult]` |
| `enroll_batch()` | `List[FaceRecognitionResult]` |
| `predict()` | `InferenceResults` (with `.faces` property) |
| `predict_batch()` | Iterator of `InferenceResults` |

### FaceTracker

| Method | Return Type |
|--------|-------------|
| `predict_batch()` | Iterator of `InferenceResults` (with `.faces` property) |
| `find_faces_in_file()` | `Dict[int, FaceAttributes]` |
| `find_faces_in_clip()` | `Dict[int, FaceAttributes]` |