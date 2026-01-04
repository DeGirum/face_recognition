# ReID Database Configuration

## Configuration Overview

`ReID_Database` is configured with two parameters:

```python
from degirum_face.reid_database import ReID_DatabasePool

db = ReID_DatabasePool.get(
    db_path="./faces.lance",          # Required: database location
    model_name="arcface_resnet100"    # Optional: model validation
)
```

**Typically initialized via FaceRecognizer/FaceTracker** - see [FaceRecognizer Configuration](../face-recognizer/configuration.md) or [FaceTracker Configuration](../face-tracker/configuration.md).

---

## Parameters

### db_path (required)

Path to the LanceDB database directory.

**Relative path:**
```python
db_path="./face_database.lance"
```

**Absolute path:**
```python
db_path="/var/lib/face_recognition/faces.lance"
```

**Windows path:**
```python
db_path="C:\\FaceRecognition\\Database\\faces.lance"
```

**Database structure:**
```
face_database.lance/
├── embeddings.lance/
├── attributes.lance/
├── images.lance/
└── _metadata.lance/
```

---

### model_name (optional)

Embedding model name for validation. Ensures database only contains embeddings from compatible models.

**Example:**
```python
# Create database with model validation
db = ReID_DatabasePool.get(
    db_path="./faces.lance",
    model_name="arcface_resnet100"
)

# Later access validates model matches
db2 = ReID_DatabasePool.get(
    db_path="./faces.lance",
    model_name="arcface_resnet100"  # ✓ Matches
)

# Different model raises ValueError
db3 = ReID_DatabasePool.get(
    db_path="./faces.lance",
    model_name="facenet_512"  # ✗ Raises ValueError
)
```

**When to use:**
- Multi-model environments
- Preventing embedding pollution
- Database migration validation

**When to omit:**
- Single-model deployments
- Testing/development

---

## Initialization Patterns

### Using ReID_DatabasePool (Recommended)

Connection pooling ensures single connection per database path:

```python
from degirum_face.reid_database import ReID_DatabasePool

# Get or create database instance
db = ReID_DatabasePool.get("./faces.lance")

# Subsequent calls return same instance
db2 = ReID_DatabasePool.get("./faces.lance")
assert db is db2  # Same connection
```

### Using ReID_Database Directly

Direct instantiation (bypasses connection pooling):

```python
from degirum_face.reid_database import ReID_Database

db = ReID_Database(
    db_path="./faces.lance",
    model_name="arcface_resnet100"  # Optional
)
```

**Warning:** Not recommended for production. Multiple instances for the same path can cause issues.

---

## Environment-Specific Paths

### Development

```python
# Local relative path
db = ReID_DatabasePool.get("./dev_faces.lance")
```

### Production

```python
# Persistent storage location
db = ReID_DatabasePool.get("/data/face_recognition/production.lance")

# Or use environment variable
import os
db_path = os.environ.get("FACE_DB_PATH", "./faces.lance")
db = ReID_DatabasePool.get(db_path)
```

### Docker/Container

```python
# Mount persistent volume to /data
db = ReID_DatabasePool.get("/data/faces.lance")
```

---

See [Methods Reference](methods.md) for database operations.
