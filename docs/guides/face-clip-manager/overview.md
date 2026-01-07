# FaceClipManager Overview

Helper class for managing video clips saved by FaceTracker.

## What is FaceClipManager?

`FaceClipManager` manages video clips saved by `FaceTracker`'s alert recording pipeline. It provides simple methods to list, download, and remove clips from object storage.

Typically used with the same `clip_storage_config` from your FaceTracker setup.

## When to Use

Use `FaceClipManager` to manage clips saved by FaceTracker:
- List alert clips saved during monitoring
- Download clips for backup
- Implement retention policies (remove old clips)
- Clean up storage after review

**Typical workflow:**
1. Configure `FaceTracker` with `clip_storage_config` and alert mode
2. Run `FaceTracker.start_face_tracking_pipeline()` - saves clips when alerts trigger
3. Use `FaceClipManager` to list/download/remove saved clips

**For analyzing clips**, use [FaceTracker.find_faces_in_clip()](../face-tracker/methods.md#find_faces_in_clip).

---

## How It Works

Initialize `FaceClipManager` with an `ObjectStorageConfig` - typically the same config used by FaceTracker:

```python
import degirum_face
import degirum_tools

# Use same storage config as FaceTracker
clip_manager = degirum_face.FaceClipManager(
    degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    )
)

# List all clips
clips = clip_manager.list_clips()

# Download a clip
clip_data = clip_manager.download_file("incident_01.mp4")

# Remove old clips
clip_manager.remove_file("old_clip.mp4")
```

See [Configuration Guide](configuration.md) for storage setup and FaceTracker integration.

See [Methods Reference](methods.md) for complete API with examples.
