# Quick Start

Build practical face recognition workflows step-by-step.

## Prerequisites

Install the package (see [main README](../../README.md) for requirements):

```bash
pip install degirum-face
```

## Task 1: Recognize Faces in Your Photos

**Goal:** Identify who appears in group photos based on enrolled reference images.

### Step 1: Enroll People

Start by adding known faces to your database:

```python
import degirum_face

# Create recognizer (defaults to CPU models)
face_recognizer = degirum_face.FaceRecognizer()

# Add people from reference photos
face_recognizer.enroll_image("john_headshot.jpg", "John")
face_recognizer.enroll_image("mary_headshot.jpg", "Mary")
face_recognizer.enroll_image("alice_photo.jpg", "Alice")

print(f"Enrolled: {face_recognizer.list_identities()}")
```

**What happens:** Each person gets enrolled with all their facial embeddings stored in a LanceDB database (`./face_db.lance`).

### Step 2: Identify Faces

Now recognize who's in your photos:

```python
# Identify faces in a group photo
result = face_recognizer.predict("group_photo.jpg")

for i, face in enumerate(result.faces):
    if face.attributes:
        print(f"Face {i+1}: {face.attributes} (confidence: {face.similarity_score:.2f})")
    else:
        print(f"Face {i+1}: Unknown person")
```

**What happens:** The system detects all faces, extracts embeddings, and matches against your enrolled database.

## Task 2: Process a Folder of Images

**Goal:** Batch process hundreds of photos to find specific people.

```python
from pathlib import Path

# Get all images in a directory
image_files = list(Path("vacation_photos/").glob("*.jpg"))

# Process all at once (faster than one-by-one)
for result in face_recognizer.predict_batch(iter(image_files)):
    matches = [f.attributes for f in result.faces if f.attributes]
    
    if "John" in matches:
        print(f"John appears in: {result.image_path}")
```

**Why batch?** `predict_batch()` is optimized for processing many images efficiently.

## Task 3: Find All Photos of a Person

**Goal:** Search your photo library for all images containing a specific person.

```python
from pathlib import Path

# Enroll the target person
face_recognizer.enroll_image("reference/target_person.jpg", "Target")

# Search all photos
matches = []
for photo in Path("photo_library/").glob("*.jpg"):
    result = face_recognizer.predict(str(photo))
    
    # Check if target person appears with high confidence
    for face in result.faces:
        if face.attributes == "Target" and face.similarity_score > 0.85:
            matches.append(photo)
            break

print(f"Found {len(matches)} photos containing Target")
```

**Tip:** Adjust `similarity_score` threshold (0.85 here) based on your accuracy needs.

## Task 4: Track Faces in Video

**Goal:** Monitor a video stream or file with real-time face recognition.

**When to use FaceTracker:** Video requires temporal tracking (same person across frames), not just frame-by-frame recognition. Use `FaceTracker` instead of `FaceRecognizer`.

```python
import degirum_face

# Create tracker with video source
config = degirum_face.FaceTrackerConfig(
    video_source="security_camera.mp4",
    db_path="./tracker_db.lance"
)
face_tracker = degirum_face.FaceTracker(config)

# Start real-time tracking
face_tracker.start_face_tracking_pipeline()
```

See [Face Tracker Quick Start](../guides/face-tracker/quickstart.md) for complete video tracking workflow.

## What You've Learned

- **Single image recognition** - `predict()` for one image at a time
- **Batch processing** - `predict_batch()` for efficient multi-image processing  
- **Database enrollment** - `enroll_image()` to add known people
- **Threshold tuning** - `similarity_score` controls match sensitivity
- **Video tracking** - Use `FaceTracker` for temporal awareness across frames

## Next Steps

**Understand the system:**
- [Basic Concepts](basic-concepts.md) - Recognition pipeline, result properties, deployment options

**Configure for your needs:**
- [Configuration Guide](../guides/face-recognizer/configuration.md) - Hardware selection, quality filters, thresholds
- [Face Filters](../reference/face-filters.md) - Filter by size, frontal pose, zone, etc.

**Advanced usage:**
- [Methods Reference](../guides/face-recognizer/methods.md) - All APIs with detailed examples
- [Face Tracker Guide](../guides/face-tracker/quickstart.md) - Complete video tracking workflow

**Working examples:**
- [examples/](../../examples/) folder - Ready-to-run Python scripts
- [Tutorials.ipynb](../../examples/Tutorials.ipynb) - Interactive Jupyter notebooks
