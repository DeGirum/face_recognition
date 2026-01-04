# Face Filters Reference

## Overview

Face filters act as **quality gates** that skip low-quality detections before running the expensive embedding model. Proper filtering improves both performance and accuracy.

### Why Use Filters?

Not every detected face should be processed:
- **Small/distant faces** - Too few pixels for reliable recognition
- **Profile/side views** - Embedding models work best on frontal faces  
- **Poor framing** - Faces cut off at edges produce unreliable embeddings
- **Outside region of interest** - Ignore faces in irrelevant areas

Filters prevent wasted compute and improve result quality.

## FaceFilterConfig

All filters are controlled through a `FaceFilterConfig` object:

```python
import degirum_face

filters = degirum_face.FaceFilterConfig(
    # Small face filter
    enable_small_face_filter=True,
    min_face_size=50,
    
    # Zone filter
    enable_zone_filter=True,
    zone=[[100, 100], [500, 100], [500, 400], [100, 400]],
    
    # Geometric filters
    enable_frontal_filter=True,
    enable_shift_filter=True,
)

# Use in configuration
config = degirum_face.FaceRecognizerConfig(
    face_filters=filters,
    # ... other config
)
```

## Filter Types

### 1. Small Face Filter

Skips faces where the bounding box is too small for reliable recognition.

#### Configuration

```python
filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=50  # Minimum pixels for shorter side of bbox
)
```

#### Parameters

- **`enable_small_face_filter`** (bool) - Enable/disable the filter
- **`min_face_size`** (int) - Minimum size in pixels for the shorter side of the bounding box

#### When to Use

- Processing images with varying camera distances
- Ignore distant/background people
- Improve accuracy by filtering unreliable small detections

#### Trade-offs

- **Higher threshold (60-80):** Faster processing, miss distant faces
- **Lower threshold (30-40):** More coverage, slower processing
- **Very high (200-400):** Maximum quality for close-up enrollment (e.g., access control)

#### Example

```python
# Access control - require close-up faces
access_control_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=200  # ~50% of 400px frame height
)

# General recognition - allow distant faces
general_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=40
)
```

---

### 2. Zone Filter

Only processes faces within a specified polygon region.

#### Configuration

```python
# Define rectangular zone
zone = [
    [100, 100],   # Top-left corner (x, y)
    [500, 100],   # Top-right corner
    [500, 400],   # Bottom-right corner
    [100, 400]    # Bottom-left corner
]

filters = degirum_face.FaceFilterConfig(
    enable_zone_filter=True,
    zone=zone  # List of [x, y] coordinates (min 3 points)
)
```

#### Parameters

- **`enable_zone_filter`** (bool) - Enable/disable the filter
- **`zone`** (list of [x, y]) - Polygon vertices defining the region of interest

#### How It Works

Face center point must be inside the polygon zone. Faces outside are skipped.

#### When to Use

- Focus on specific areas (doorway, checkout counter, entrance)
- Ignore people outside region of interest
- Reduce false positives from background activity

#### Examples

**Rectangular zone:**
```python
# Rectangle from (100,100) to (500,400)
zone = [[100, 100], [500, 100], [500, 400], [100, 400]]
```

**Arbitrary polygon:**
```python
# Pentagonal zone
zone = [[100, 200], [300, 100], [500, 200], [400, 400], [200, 400]]
```

**Entire frame (no filtering):**
```python
# Don't enable zone filter, or use full frame dimensions
zone = [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]
```

---

### 3. Frontal Filter

Only processes faces looking roughly toward the camera (frontal view).

#### Configuration

```python
filters = degirum_face.FaceFilterConfig(
    enable_frontal_filter=True
)
```

#### Parameters

- **`enable_frontal_filter`** (bool) - Enable/disable the filter

#### How It Works

Checks if nose keypoint is inside the rectangle formed by eyes and mouth. Profiles/side views fail this test.

#### When to Use

- Need high-quality embeddings (frontal faces work best)
- Access control where users face the camera
- Reduce processing of profile/side views
- Improve recognition accuracy

#### Trade-offs

- **Enabled:** Better quality, miss non-frontal faces
- **Disabled:** Process all angles, lower quality for profiles

#### Example

```python
# Security checkpoint - require frontal faces
security_filters = degirum_face.FaceFilterConfig(
    enable_frontal_filter=True,
    enable_small_face_filter=True,
    min_face_size=150
)

# Photo album - accept all angles
photo_filters = degirum_face.FaceFilterConfig(
    enable_frontal_filter=False,  # Accept profiles
    enable_small_face_filter=True,
    min_face_size=40
)
```

---

### 4. Shift Filter

Skips faces that are poorly framed (cut off at image edges or off-center).

#### Configuration

```python
filters = degirum_face.FaceFilterConfig(
    enable_shift_filter=True
)
```

#### Parameters

- **`enable_shift_filter`** (bool) - Enable/disable the filter

#### How It Works

Rejects faces where facial keypoints are clustered to one side of the bounding box (indicates face is cut off or poorly framed).

#### When to Use

- Avoid processing partially visible faces
- Improve embedding quality by filtering edge cases
- Video scenarios where people enter/exit frame
- Ensure complete face is visible

#### Trade-offs

- **Enabled:** Higher quality, miss partially visible faces
- **Disabled:** Process all detections, some may be cut off

#### Example

```python
# Video monitoring - skip people entering/exiting
video_filters = degirum_face.FaceFilterConfig(
    enable_shift_filter=True,  # Skip partial faces
    enable_frontal_filter=True,
)

# Static photos - process even if slightly cut off
photo_filters = degirum_face.FaceFilterConfig(
    enable_shift_filter=False,  # Allow edge cases
)
```

---

### 5. ReID Expiration Filter

**Note:** This filter is specific to `FaceTracker` and video tracking workflows. It does not affect `FaceRecognizer` which processes static images.

Reduces embedding extraction frequency using **adaptive exponential backoff** for continuously tracked faces.

#### Configuration

```python
filters = degirum_face.FaceFilterConfig(
    enable_reid_expiration_filter=True,
    reid_expiration_frames=30  # Maximum interval
)
```

#### Parameters

- **`enable_reid_expiration_filter`** (bool) - Enable/disable the ReID expiration filter (default: True)
- **`reid_expiration_frames`** (int) - Maximum interval in frames between embedding extractions for stable tracks (default: 30)

#### How It Works

When enabled, the filter adaptively increases the interval between embedding extractions for continuously tracked faces:

```
Frame 1:  New face → Extract embedding (interval: 1 frame)
Frame 2:  Same face → Extract embedding (interval: 1 frame)
Frame 4:  Same face → Extract embedding (interval: 2 frames)
Frame 8:  Same face → Extract embedding (interval: 4 frames)
Frame 16: Same face → Extract embedding (interval: 8 frames)
Frame 32: Same face → Extract embedding (interval: 16 frames)
Frame 62: Same face → Extract embedding (interval: 30 frames, maxed out at reid_expiration_frames)
Frame 92: Same face → Extract embedding (interval: 30 frames)
...stays at reid_expiration_frames interval
```

**Result:** For a face tracked over 100 frames, extracts ~7 embeddings instead of 100 (14x reduction).

#### When to Use

- Real-time video tracking with `FaceTracker`
- Reduce computational cost for stable, continuously tracked faces
- Maintain accuracy while improving performance

#### Tuning `reid_expiration_frames`

- **Static scenes** (office entry, checkpoint): `reid_expiration_frames=60` - Stable faces, can wait longer between embeddings
- **Dynamic scenes** (retail, crowds): `reid_expiration_frames=15` - Quick movements, need more frequent updates
- **Recommended default:** `30` frames (~1 second at 30 FPS)

#### When Embedding Extraction Happens

- New track detected (first frame)
- Expiration timer reached (adaptive interval: 1, 2, 4, 8... up to max)
- Track ID re-acquired after loss
- Quality filters passed after previous failure

#### Trade-offs

- **Higher value (60+):** Fewer embeddings, faster FPS, slower response to face angle changes
- **Lower value (10-20):** More embeddings, slower FPS, quicker response to movement

#### Example

```python
# Static scene - maximize performance
static_filters = degirum_face.FaceFilterConfig(
    enable_reid_expiration_filter=True,
    reid_expiration_frames=60  # Wait longer between embeddings
)

# Dynamic scene - maintain responsiveness  
dynamic_filters = degirum_face.FaceFilterConfig(
    enable_reid_expiration_filter=True,
    reid_expiration_frames=15  # More frequent updates
)
```

**Important:** This filter only works with `FaceTracker` for continuous video streams. It has no effect on `FaceRecognizer.predict_batch()` since there are no persistent track IDs across batch items.

---

## Combining Filters

Filters work in conjunction - a face must pass **ALL enabled filters** to be processed.

### Strict Filtering

For high-quality, reliable results:

```python
strict_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=80,              # Larger faces only
    enable_frontal_filter=True,     # Frontal views only
    enable_shift_filter=True,       # Well-framed only
    enable_zone_filter=True,        # Specific area only
    zone=[[200, 150], [600, 150], [600, 450], [200, 450]]
)
```

**Use for:** Access control, security applications, enrollment

### Balanced Filtering

For general use:

```python
balanced_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=50,              # Moderate size
    enable_frontal_filter=True,     # Prefer frontal
    enable_shift_filter=False,      # Allow some edge cases
)
```

**Use for:** Photo organization, general recognition

### Permissive Filtering

For maximum coverage:

```python
permissive_filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=30,              # Small threshold
    enable_frontal_filter=False,    # All angles
    enable_shift_filter=False,      # All framing
)
```

**Use for:** Photo search, surveillance (wide coverage)

---

## Configuration Methods

### Python Configuration

```python
import degirum_face

filters = degirum_face.FaceFilterConfig(
    enable_frontal_filter=True,
    enable_small_face_filter=True,
    min_face_size=60
)

config = degirum_face.FaceRecognizerConfig(
    face_detection_model_spec=degirum_face.get_face_detection_model_spec("TFLITE/CPU"),
    face_embedding_model_spec=degirum_face.get_face_embedding_model_spec("TFLITE/CPU"),
    db_path="./face_db.lance",
    face_filters=filters,
)
```

### YAML Configuration

```yaml
face_filters:
  enable_frontal_filter: true
  enable_small_face_filter: true
  min_face_size: 60
  enable_shift_filter: true
  enable_zone_filter: true
  zone:
    - [100, 100]
    - [500, 100]
    - [500, 400]
    - [100, 400]
```

---

## Use Case Recommendations

### Access Control / Security

```python
filters = degirum_face.FaceFilterConfig(
    enable_frontal_filter=True,     # Ensure clear view
    enable_small_face_filter=True,
    min_face_size=200,              # Close-up required (~50% frame)
    enable_shift_filter=True,       # Complete face visible
    enable_zone_filter=True,        # Specific entry zone
    zone=[[300, 200], [700, 200], [700, 600], [300, 600]]
)
```

### Video Surveillance

```python
filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=50,               # Moderate distance
    enable_frontal_filter=True,      # Better accuracy
    enable_shift_filter=True,        # Skip entering/exiting
)
```

### Photo Organization

```python
filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=40,               # Allow distant faces
    enable_frontal_filter=False,    # All angles accepted
    enable_shift_filter=False,      # Edge cases OK
)
```

### Maximum Coverage

```python
filters = degirum_face.FaceFilterConfig(
    enable_small_face_filter=True,
    min_face_size=30,               # Very small allowed
    # All geometric filters disabled
)
```

---

## Filter Tuning Guide

1. **Start with balanced defaults:**
   - `min_face_size=50`
   - `enable_frontal_filter=True`
   - Other filters disabled

2. **Test with real data:**
   - Process representative images
   - Check what's being filtered
   - Measure accuracy and performance

3. **Adjust based on results:**
   - **Too many false positives?** Enable more filters or increase thresholds
   - **Missing valid faces?** Relax filters or lower thresholds
   - **Too slow?** Increase `min_face_size` to skip more faces

4. **Consider your use case:**
   - Security: Strict filtering
   - General use: Balanced filtering
   - Search/discovery: Permissive filtering
