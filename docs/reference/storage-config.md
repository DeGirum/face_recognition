# Object Storage Configuration Reference

## Overview

`ObjectStorageConfig` from `degirum_tools` is used for storing and managing files in S3-compatible storage. Supports AWS S3, MinIO, local filesystem, and any S3-compatible service.

### Where It's Used

- **[FaceTracker](../guides/face-tracker/configuration.md#clip-storage)** - `clip_storage_config` for saving video clips
- **[FaceClipManager](../guides/face-clip-manager/configuration.md)** - Managing saved clips

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | str | Yes | Storage endpoint (URL for S3/MinIO, or local path) |
| `bucket` | str | Yes | Bucket name or folder name |
| `access_key` | str | No | Access key ID (required for S3/MinIO) |
| `secret_key` | str | No | Secret access key (required for S3/MinIO) |
| `url_expiration_s` | int | No | Presigned URL expiration in seconds (default: 3600) |

---

## Configuration Examples

### Local Storage

Store files in a local directory:

```python
import degirum_tools
from pathlib import Path

# IMPORTANT: Create the directory before using it
endpoint_path = Path("./clips")
endpoint_path.mkdir(parents=True, exist_ok=True)

storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="./clips",
    bucket="alerts"
)
```

Files are saved to: `./clips/alerts/`

**⚠️ Important:** The endpoint directory **must exist** before configuration. If the path doesn't exist, the system treats it as an S3 bucket endpoint and will fail with a "path not allowed" error.

**Use for:**
- Development and testing
- Single-machine deployments
- Simple file storage needs

---

### AWS S3

Store files in AWS S3 bucket:

```python
import os
import degirum_tools

storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="s3.amazonaws.com",
    access_key=os.environ["AWS_ACCESS_KEY_ID"],
    secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    bucket="security-footage"
)
```

**Best practices:**
- Use environment variables for credentials
- Prefer IAM roles when running on AWS EC2
- Never hardcode credentials in code
- Use bucket policies for access control

**Use for:**
- Production deployments
- Multi-region access
- Scalable cloud storage

---

### MinIO

Store files in MinIO (self-hosted S3):

```python
import degirum_tools

storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="minio.local:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket="surveillance-clips"
)
```

**Use for:**
- Development and testing
- On-premise deployments
- Data sovereignty requirements
- S3-compatible storage without cloud costs

---

### S3-Compatible Services

Works with any S3-compatible service (Wasabi, DigitalOcean Spaces, Backblaze B2, etc.):

```python
import os
import degirum_tools

storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="s3.us-east-1.wasabisys.com",
    access_key=os.environ["WASABI_ACCESS_KEY"],
    secret_key=os.environ["WASABI_SECRET_KEY"],
    bucket="video-archive"
)
```

**Use for:**
- Cost-optimized storage (Wasabi, Backblaze)
- Regional storage providers
- Alternative cloud providers

---

## Usage Examples

### FaceTracker with Clip Storage

```python
import degirum_face
import degirum_tools

tracker_config = degirum_face.FaceTrackerConfig(
    # ... model specs and db_path ...
    alert_mode=degirum_face.AlertMode.ON_UNKNOWNS,
    clip_duration=150,
    clip_storage_config=degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    )
)

tracker = degirum_face.FaceTracker(tracker_config)
```

### FaceClipManager

```python
import degirum_face
import degirum_tools

# Typically uses same config as FaceTracker
clip_manager = degirum_face.FaceClipManager(
    tracker_config.clip_storage_config
)

# Or create independently
clip_manager = degirum_face.FaceClipManager(
    degirum_tools.ObjectStorageConfig(
        endpoint="./security_clips",
        bucket="unknowns"
    )
)
```

---

## Environment-Specific Configurations

### Development

```python
# Local filesystem for easy debugging
storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="./dev_clips",
    bucket="test"
)
```

### Staging

```python
# MinIO for S3-compatible testing
storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="minio.staging:9000",
    access_key=os.environ["MINIO_ACCESS_KEY"],
    secret_key=os.environ["MINIO_SECRET_KEY"],
    bucket="staging-clips"
)
```

### Production

```python
# AWS S3 with IAM roles (no hardcoded credentials)
storage_config = degirum_tools.ObjectStorageConfig(
    endpoint="s3.amazonaws.com",
    access_key=os.environ["AWS_ACCESS_KEY_ID"],
    secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    bucket="production-security-footage"
)
```
