# ReID Database Overview

LanceDB-based storage for face embeddings and attributes.

## What is ReID Database?

`ReID_Database` is the underlying storage layer for face embeddings and person attributes in `degirum-face`. It uses LanceDB to store:
- Face embedding vectors for similarity search
- Person attributes (names, metadata)
- Associated face images
- Model metadata for validation

The database is automatically managed by `FaceRecognizer` and `FaceTracker` - you typically don't instantiate it directly.

## When to Use

**Automatic usage** - The database is created and managed when you initialize `FaceRecognizer` or `FaceTracker`:

```python
# Database created automatically at db_path
recognizer = degirum_face.FaceRecognizer(
    config=degirum_face.FaceRecognizerConfig(
        db_path="./my_faces.lance",  # Database location
        # ...
    )
)
```

**Direct usage** - Only needed for:
- Custom database operations
- Database migration/backup tools
- Advanced batch processing
- Direct embedding management

## How It Works

The database uses LanceDB with four internal tables:

| Table | Purpose |
|-------|---------|
| `embeddings` | Face embedding vectors with image references |
| `attributes` | Person metadata (names, IDs) |
| `images` | Face image storage (PNG format) |
| `_metadata` | Model validation metadata |

**Key features:**
- **Vector search** - Fast similarity search using cosine distance
- **Deduplication** - Automatic embedding deduplication via hashing
- **Thread-safe** - Safe for concurrent access
- **Model validation** - Ensures embeddings from same model
- **Connection pooling** - Single connection per database path

See [Configuration Guide](configuration.md) for database initialization options.

See [Methods Reference](methods.md) for complete API.
