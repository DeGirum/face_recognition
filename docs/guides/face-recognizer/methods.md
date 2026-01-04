# FaceRecognizer Methods

**Note:** Examples in this guide assume you have already configured `FaceRecognizerConfig` with model specifications. See [Configuration Guide](configuration.md) for complete setup details.

## Methods Overview

| Method | Purpose | Input | Best For |
|--------|---------|-------|----------|
| `enroll_image()` | Add single face to database | One image, one name | Interactive enrollment |
| `enroll_batch()` | Add multiple faces to database | Image iterator, names | Bulk enrollment |
| `predict()` | Recognize faces in one image | One image | Single photo processing |
| `predict_batch()` | Recognize faces in multiple images | Image iterator | Video/batch processing |

**Performance tip:** Use `_batch()` methods for multiple items - they provide ~2-3x speedup through pipeline parallelism.

## FaceRecognitionResult

`FaceRecognitionResult` objects represent detected faces with their properties. Returned directly by enrollment methods and contained in prediction results.

**Key properties:** `attributes`, `similarity_score`, `bbox`, `embeddings`, `images`

See [FaceRecognitionResult Reference](../../reference/face-recognition-result.md) for complete property list and usage examples.

---

## enroll_image()

Enroll a single person's face from one image.

### Signature

```python
enroll_image(frame: Any, attributes: Any) -> Optional[FaceRecognitionResult]
```

### Parameters

- **`frame`** - Image as numpy array or file path (str)
- **`attributes`** - Person identifier (typically a name string)

### Returns

- `Optional[FaceRecognitionResult]` - Face recognition result for the enrolled face, or `None` if no face was detected. See [FaceRecognitionResult Reference](../../reference/face-recognition-result.md)

### How It Works

1. Detects all faces in the image
2. Selects the largest face (by bounding box area)
3. Extracts face embedding
4. Stores embedding in database with the provided attributes

### Examples

**Enroll from file path:**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

result = face_recognizer.enroll_image('photos/alice.jpg', 'Alice')
if result:
    print(f"Enrolled {result.attributes}")
    print(f"Embedding shape: {result.embeddings[0].shape}")
# Output: Enrolled Alice
#         Embedding shape: (512,)
```

**Enroll from numpy array:**
```python
import degirum_face
import cv2

face_recognizer = degirum_face.FaceRecognizer()

image = cv2.imread('photos/bob.jpg')
result = face_recognizer.enroll_image(image, 'Bob')
```

**Enroll multiple photos of same person:**
```python
# Better accuracy with multiple views
face_recognizer.enroll_image('alice_front.jpg', 'Alice')
face_recognizer.enroll_image('alice_side.jpg', 'Alice')
face_recognizer.enroll_image('alice_smile.jpg', 'Alice')
```

### Best Practices

- **Use clear, frontal face images** for best enrollment quality
- **One person per image** - If multiple faces present, largest is selected
- **Enroll multiple photos** per person from different angles/lighting
- **Consistent naming** - Use the same `attributes` value for the same person

---

## enroll_batch()

Enroll multiple faces from multiple images efficiently.

### Signature

```python
enroll_batch(frames: Iterable, attributes: Iterable) -> List[FaceRecognitionResult]
```

### Parameters

- **`frames`** - Iterable of images (file paths or numpy arrays)
- **`attributes`** - Iterable of person identifiers (must match frames order)

### Returns

- `List[FaceRecognitionResult]` - List of face recognition results for enrolled faces (frames with no detected faces are skipped). See [FaceRecognitionResult Reference](../../reference/face-recognition-result.md)

### How It Works

1. Processes all images through detection → embedding pipeline
2. For each image, selects largest face
3. Stores each embedding with corresponding attributes
4. **Pipeline parallelism** makes this faster than calling `enroll_image()` repeatedly

### Examples

**Enroll multiple people:**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Prepare data
image_paths = ['alice1.jpg', 'bob1.jpg', 'charlie1.jpg']
names = ['Alice', 'Bob', 'Charlie']

# Enroll all at once
results = face_recognizer.enroll_batch(
    frames=iter(image_paths),
    attributes=iter(names)
)

print(f"Enrolled {len(results)} people")
for result in results:
    print(f"  - {result.attributes}")
# Output: Enrolled 3 people
#           - Alice
#           - Bob
#           - Charlie
```

**Enroll multiple photos of same person:**
```python
# Improve recognition accuracy with varied poses/lighting
alice_photos = ['alice1.jpg', 'alice2.jpg', 'alice3.jpg']
alice_names = ['Alice', 'Alice', 'Alice']  # Same name repeated

results = face_recognizer.enroll_batch(
    frames=iter(alice_photos),
    attributes=iter(alice_names)
)

print(f"Enrolled {len(results)} embeddings for Alice")
# Output: Enrolled 3 embeddings for Alice
```

**Bulk enrollment from directory:**
```python
from pathlib import Path

# Assume directory structure: photos/person_name/image.jpg
photo_dir = Path("enrollment_photos/")

frames = []
attributes = []

for person_dir in photo_dir.iterdir():
    if person_dir.is_dir():
        person_name = person_dir.name
        for photo in person_dir.glob("*.jpg"):
            frames.append(str(photo))
            attributes.append(person_name)

# Enroll everyone
results = face_recognizer.enroll_batch(
    frames=iter(frames),
    attributes=iter(attributes)
)

print(f"Successfully enrolled {len(results)} faces")
```

### Best Practices

- **Always use iterators:** `iter(list)` not just `list`
- **Match lengths:** Ensure `frames` and `attributes` have same length
- **Multiple photos per person:** Improves accuracy across different conditions
- **Use batch for 3+ enrollments:** Performance benefit over individual calls

---

## predict()

Recognize all faces in a single image.

### Signature

```python
predict(frame: Any) -> InferenceResults
```

### Parameters

- **`frame`** - Image as numpy array or file path (str)

### Returns

- `InferenceResults` - Object with `.faces` property containing list of `FaceRecognitionResult` objects. See [FaceRecognitionResult Reference](../../reference/face-recognition-result.md) for properties. InferenceResults objects support standard PySDK methods like `image_overlay()`, `results`, etc. See [InferenceResults documentation](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor)

### Examples

**Basic recognition:**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll known faces
face_recognizer.enroll_image('alice.jpg', 'Alice')
face_recognizer.enroll_image('bob.jpg', 'Bob')

# Recognize faces
result = face_recognizer.predict('group_photo.jpg')

print(f"Found {len(result.faces)} faces")
for face in result.faces:
    if face.attributes:
        print(f"- {face.attributes} ({face.similarity_score:.2f})")
    else:
        print(f"- Unknown person")
```

**Access all face properties:**
```python
result = face_recognizer.predict('test.jpg')

for i, face in enumerate(result.faces):
    print(f"\nFace {i+1}:")
    print(f"  Person: {face.attributes}")
    print(f"  Match confidence: {face.similarity_score:.2f}" if face.similarity_score else "  Unknown")
    print(f"  Detection confidence: {face.detection_score:.2f}")
    print(f"  Bounding box: {face.bbox}")
    print(f"  Database ID: {face.db_id}")
    print(f"  Cropped images: {len(face.images)}")
```

**Pretty print (uses `__str__()`):**
```python
result = face_recognizer.predict('test.jpg')

for face in result.faces:
    print(face)  # Formatted output
    print()      # Blank line
```

**Example output:**
```
Attributes      : Alice
Database ID     : 2a3f7c9e
Detection Score : 0.987
Similarity Score: 0.823
Bounding box    : [245, 120, 389, 298]
Landmarks       : 5 points
Embeddings      : 1 vector(s)

Attributes      : None
Database ID     : None
Detection Score : 0.952
Similarity Score: None
Bounding box    : [512, 95, 645, 267]
Landmarks       : 5 points
Embeddings      : 1 vector(s)
```

**Filter by confidence:**
```python
result = face_recognizer.predict('photo.jpg')

# Only show high-confidence matches
for face in result.faces:
    if face.attributes and face.similarity_score > 0.75:
        print(f"High confidence: {face.attributes} ({face.similarity_score:.2f})")
```

**Access cropped face images:**
```python
import cv2

result = face_recognizer.predict('photo.jpg')

for i, face in enumerate(result.faces):
    if face.images:
        # face.images contains cropped face images as numpy arrays
        cropped_face = face.images[0]  # Get first (or only) crop
        
        # Save cropped face to disk
        if face.attributes:
            cv2.imwrite(f"face_{face.attributes}_{i}.jpg", cropped_face)
        else:
            cv2.imwrite(f"face_unknown_{i}.jpg", cropped_face)
```

**Note:** The `images` list contains aligned and cropped face images (typically 112×112) that were used for embedding extraction. These are useful for:
- Visual verification of detected faces
- Creating face galleries or thumbnails
- Quality assurance and debugging
- Building custom datasets

### When to Use

- Processing individual photos
- Simple recognition tasks
- Testing and debugging
- Real-time single-frame analysis

---

## predict_batch()

Recognize faces across multiple images or video efficiently using pipeline parallelism.

### Signature

```python
predict_batch(frames: Iterable) -> Iterator[InferenceResults]
```

### Parameters

- **`frames`** - Iterable of images (file paths, numpy arrays) or video frames from generator

### Returns

- `Iterator[InferenceResults]` - Iterator yielding results for each input frame. InferenceResults objects support standard PySDK methods like `image_overlay()`, `results`, etc. See [InferenceResults documentation](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor) for complete API reference.

### How It Works

1. Accepts iterator/generator yielding frames
2. Processes frames through detection → embedding → matching pipeline
3. Yields results as they're ready (streaming)
4. **Pipeline parallelism** provides ~2-3x speedup over calling `predict()` in a loop

### Examples

**Example 1: Multiple image files**
```python
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll known faces
face_recognizer.enroll_image('alice.jpg', 'Alice')
face_recognizer.enroll_image('bob.jpg', 'Bob')

# Process multiple images
image_paths = ['photo1.jpg', 'photo2.jpg', 'photo3.jpg']

for i, result in enumerate(face_recognizer.predict_batch(iter(image_paths))):
    print(f"\nImage {i+1}: Found {len(result.faces)} faces")
    for face in result.faces:
        if face.attributes:
            print(f"  - {face.attributes} (confidence: {face.similarity_score:.2f})")
        else:
            print(f"  - Unknown person")
```

**Example 2: Video streams (recommended)**

For video files, webcams, or RTSP streams, use `degirum_tools` video helpers:

```python
import degirum_face
from degirum_tools import open_video_stream, video_source, Display

face_recognizer = degirum_face.FaceRecognizer()

# Enroll known faces
face_recognizer.enroll_image('alice.jpg', 'Alice')
face_recognizer.enroll_image('bob.jpg', 'Bob')

# Process video stream
# Supports: webcam (0), video file ('video.mp4'), RTSP ('rtsp://...')
with Display("Face Recognition") as display, open_video_stream(0) as stream:
    for result in face_recognizer.predict_batch(video_source(stream, fps=5)):
        display.show(result)
        
        # Access recognized faces
        for face in result.faces:
            if face.attributes:
                print(f"Recognized: {face.attributes} ({face.similarity_score:.2f})")
```

**Video source options:**
- **Webcam:** `open_video_stream(0)` - Index 0, 1, 2, etc.
- **Video file:** `open_video_stream('video.mp4')`
- **RTSP stream:** `open_video_stream('rtsp://192.168.1.100/stream')`
- **FPS control:** `video_source(stream, fps=5)` - Process N frames/sec

**Example 3: Custom frame generator**

Define your own generator for custom preprocessing or frame selection:

```python
import cv2
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

def custom_frame_generator():
    """Process only specific frames with custom preprocessing"""
    cap = cv2.VideoCapture('video.mp4')
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 10th frame
        if frame_count % 10 == 0:
            # Optional: resize, crop, or preprocess
            resized = cv2.resize(frame, (1280, 720))
            yield resized
        
        frame_count += 1
    
    cap.release()

# Process with custom generator
for result in face_recognizer.predict_batch(custom_frame_generator()):
    print(f"Faces: {len(result.faces)}")
```

**Example 4: Batch directory processing**
```python
from pathlib import Path
import degirum_face

face_recognizer = degirum_face.FaceRecognizer()

# Enroll known faces
face_recognizer.enroll_image('alice.jpg', 'Alice')

# Process all images in directory
photo_dir = Path("photo_library/")
image_paths = list(photo_dir.glob("*.jpg"))

# Find all photos containing Alice
alice_photos = []
for img_path, result in zip(image_paths, face_recognizer.predict_batch(iter(image_paths))):
    for face in result.faces:
        if face.attributes == "Alice" and face.similarity_score > 0.75:
            alice_photos.append(str(img_path))
            break

print(f"Found Alice in {len(alice_photos)} photos")
```

### Performance Benefits

- **~2-3x faster** than calling `predict()` in a loop
- Pipeline stages run in parallel (detection, embedding, matching)
- Ideal for video streams and high-throughput batch processing
- Streaming results (memory efficient)

### Best Practices

- **For video:** Use `degirum_tools.video_source()` - handles webcam, files, RTSP automatically
- **For images:** Use `iter(image_list)` to convert list to iterator
- **Custom needs:** Define your own generator for preprocessing or frame skipping
- **FPS control:** Use `fps=N` parameter in `video_source()` to control processing rate
- **Tracking:** For persistent face IDs across frames, consider using [FaceTracker](../face-tracker/overview.md) instead

---