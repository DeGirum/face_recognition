# FaceClipManager Methods

**Note:** FaceClipManager is a storage management utility. For face analysis of clips, use `FaceTracker.find_faces_in_clip()`. See [FaceTracker Methods](../face-tracker/methods.md).

## Methods Overview

| Method | Purpose | Use Case |
|--------|---------|----------|
| **`list_clips()`** | List all clips in storage | Inventory management, batch processing |
| **`download_file()`** | Download clip from storage | Local review, backup |
| **`remove_file()`** | Delete clip from storage | Cleanup, retention management |
| **`remove_all_clips()`** | Clear all clips from storage | Complete cleanup (use with caution) |

---

## list_clips()

List all video clips and their related files in object storage.

**When to use:** Use this to inventory what's stored, find specific clips, or iterate through all clips for batch operations. The method groups related files (original, annotated, JSON) by base name.

### Signature

```python
list_clips() -> Dict[str, dict]
```

### Returns

Dictionary mapping clip base names to file objects:
- `"original"` - Original video clip file (`.mp4`)
- `"annotated"` - Annotated video clip (if exists, `_annotated.mp4`)
- `"json"` - JSON annotations file (if exists, `.json`)

Each file object is of type `minio.datatypes.Object` with properties:
- `object_name` - Full path in storage
- `size` - File size in bytes
- `last_modified` - Timestamp of last modification

### Example: Inventory Clips

```python
import degirum_face
import degirum_tools
import os

storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="s3.amazonaws.com",
    access_key=os.environ["AWS_ACCESS_KEY_ID"],
    secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    bucket="security-footage"
)
clip_manager = degirum_face.FaceClipManager(storage_config)

clips = clip_manager.list_clips()

print(f"Total clips: {len(clips)}")
print("\nClip inventory:")

for clip_name, files in clips.items():
    print(f"\n{clip_name}:")
    
    if "original" in files:
        orig = files["original"]
        print(f"  Original: {orig.object_name} ({orig.size / 1024 / 1024:.1f} MB)")
    
    if "annotated" in files:
        anno = files["annotated"]
        print(f"  Annotated: {anno.object_name} ({anno.size / 1024 / 1024:.1f} MB)")
    
    if "json" in files:
        print(f"  JSON: {files['json'].object_name}")
```

### Example: Find Recent Clips

```python
from datetime import datetime, timedelta

clips = clip_manager.list_clips()

# Find clips from last 24 hours
recent_threshold = datetime.now() - timedelta(days=1)
recent_clips = []

for clip_name, files in clips.items():
    if "original" in files:
        if files["original"].last_modified >= recent_threshold:
            recent_clips.append(clip_name)

print(f"Recent clips (last 24h): {len(recent_clips)}")
for clip in recent_clips:
    print(f"  - {clip}")
```

### Example: Find Clips Missing Annotations

```python
clips = clip_manager.list_clips()

missing_annotations = []
for clip_name, files in clips.items():
    if "original" in files and "annotated" not in files:
        missing_annotations.append(clip_name)

print(f"Clips without annotations: {len(missing_annotations)}")
for clip in missing_annotations:
    print(f"  - {clip}")
```

---

## download_file()

Download a video clip or related file from object storage.

**When to use:** Use this to retrieve clips for local review, backup, or processing. The method automatically adds `.mp4` extension if missing.

### Signature

```python
download_file(filename: str) -> bytes
```

### Parameters

- **`filename`** (str) - Name of file to download (`.mp4` extension optional)

### Returns

- `bytes` - Raw bytes of the downloaded file

### Example: Download and Save

```python
import degirum_face
import degirum_tools

storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="./clips",
    bucket="alerts"
)
clip_manager = degirum_face.FaceClipManager(storage_config)

# Download clip
clip_bytes = clip_manager.download_file("incident_01")  # .mp4 added automatically

# Save locally
with open("incident_local.mp4", "wb") as f:
    f.write(clip_bytes)
    
print(f"Downloaded {len(clip_bytes) / 1024 / 1024:.1f} MB")
```

### Example: Backup All Clips

```python
from pathlib import Path

# Create backup directory
backup_dir = Path("./backup")
backup_dir.mkdir(exist_ok=True)

# Download all clips
clips = clip_manager.list_clips()

for clip_name in clips.keys():
    print(f"Backing up: {clip_name}")
    
    clip_data = clip_manager.download_file(clip_name)
    backup_path = backup_dir / f"{clip_name}.mp4"
    
    with open(backup_path, "wb") as f:
        f.write(clip_data)
    
    print(f"  Saved to {backup_path}")
```

### Example: Download Both Original and Annotated

```python
clips = clip_manager.list_clips()

for clip_name, files in clips.items():
    if "original" in files and "annotated" in files:
        # Download original
        original_data = clip_manager.download_file(clip_name + ".mp4")
        with open(f"{clip_name}_original.mp4", "wb") as f:
            f.write(original_data)
        
        # Download annotated
        annotated_data = clip_manager.download_file(clip_name + "_annotated.mp4")
        with open(f"{clip_name}_annotated.mp4", "wb") as f:
            f.write(annotated_data)
        
        print(f"Downloaded both versions of {clip_name}")
```

---

## remove_file()

Remove a file from object storage.

**When to use:** Use this for cleanup after reviewing clips, implementing retention policies, or removing specific unwanted recordings. Be careful as deletion is permanent.

### Signature

```python
remove_file(filename: str)
```

### Parameters

- **`filename`** (str) - Name of file to remove (`.mp4` extension optional)

### Example: Remove Single Clip

```python
import degirum_face
import degirum_tools

storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="./clips",
    bucket="temp"
)
clip_manager = degirum_face.FaceClipManager(storage_config)

# Remove processed clip
clip_manager.remove_file("reviewed_clip_01.mp4")
print("Clip removed")
```

### Example: Retention Policy (30 Days)

```python
from datetime import datetime, timedelta

# Remove clips older than 30 days
retention_days = 30
cutoff_date = datetime.now() - timedelta(days=retention_days)

clips = clip_manager.list_clips()
removed_count = 0

for clip_name, files in clips.items():
    if "original" in files:
        clip_date = files["original"].last_modified
        
        if clip_date < cutoff_date:
            print(f"Removing old clip: {clip_name}")
            clip_manager.remove_file(clip_name)
            removed_count += 1

print(f"Removed {removed_count} clips older than {retention_days} days")
```

### Example: Remove Only Annotated Versions

```python
# Keep originals, remove annotated versions to save space
clips = clip_manager.list_clips()

for clip_name, files in clips.items():
    if "annotated" in files:
        print(f"Removing annotated version of {clip_name}")
        clip_manager.remove_file(clip_name + "_annotated.mp4")

print("All annotated versions removed, originals preserved")
```

---

## remove_all_clips()

Remove all clips and related files from object storage.

**When to use:** Use this for complete cleanup of storage bucket, clearing test data, or resetting after batch processing. **Use with extreme caution** as this deletes everything in the bucket.

### Signature

```python
remove_all_clips()
```

### Example: Clear Test Data

```python
import degirum_face
import degirum_tools

# Test/development storage only!
storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="./test_clips",
    bucket="dev_testing"
)
clip_manager = degirum_face.FaceClipManager(storage_config)

# List what will be deleted
clips = clip_manager.list_clips()
print(f"About to delete {len(clips)} clips")

# Confirm before proceeding
response = input("Are you sure? (yes/no): ")
if response.lower() == "yes":
    clip_manager.remove_all_clips()
    print("All clips removed")
else:
    print("Cancelled")
```

### Example: Cleanup After Batch Processing

```python
# After processing all clips and saving results elsewhere
clips = clip_manager.list_clips()
print(f"Processed {len(clips)} clips")

# Archive important data first (your custom code)
# backup_to_archive(clips)

# Clear storage for next batch
clip_manager.remove_all_clips()
print("Storage cleared for next batch")
```

**Warning:** This method deletes all clips in the configured bucket. There is no undo. Always verify you're connected to the correct storage before calling this method.
