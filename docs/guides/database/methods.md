# ReID Database Methods

**Note:** The database is typically managed automatically by FaceRecognizer and FaceTracker. Direct usage is only needed for advanced scenarios.

## Methods Overview

### Object Management
| Method | Purpose |
|--------|---------|
| **`add_object()`** | Add/update person attributes |
| **`get_id_by_attributes()`** | Get object ID by attributes |
| **`get_attributes_by_id()`** | Get attributes by object ID |
| **`list_objects()`** | List all objects |
| **`remove_object_by_id()`** | Remove object and embeddings |
| **`remove_object_by_attributes()`** | Remove object by attributes |

### Embedding Management
| Method | Purpose |
|--------|---------|
| **`add_embeddings()`** | Add embeddings for object ID |
| **`add_embeddings_for_attributes()`** | Add embeddings for attributes |
| **`get_embeddings()`** | Get embeddings and images |
| **`remove_embeddings_by_id()`** | Remove embeddings by ID |
| **`remove_embeddings_by_attributes()`** | Remove embeddings by attributes |
| **`count_embeddings()`** | Count embeddings per object |

### Search
| Method | Purpose |
|--------|---------|
| **`get_attributes_by_embedding()`** | Find person by embedding vector |

### Database Operations
| Method | Purpose |
|--------|---------|
| **`backup()`** | Create zip backup |
| **`restore()`** | Restore from backup |
| **`clear_all_tables()`** | Clear all data |

---

## Object Management

### add_object()

Add or update person attributes.

```python
add_object(object_id: str, attributes: Any)
```

**Parameters:**
- `object_id` (str) - Unique object ID (typically UUID)
- `attributes` (Any) - Person attributes (name, metadata, etc.)

**Example:**

```python
from degirum_face.reid_database import ReID_DatabasePool
import uuid

db = ReID_DatabasePool.get("./faces.lance")

# Add new person with simple string attribute
person_id = str(uuid.uuid4())
db.add_object(person_id, "Alice")

# Update attributes
db.add_object(person_id, "Alice Smith")
```

**Example with dictionary attributes:**

```python
# First enrollment with dict attributes - defines database structure
person1_id = str(uuid.uuid4())
db.add_object(person1_id, {
    "first_name": "Alice",
    "last_name": "Smith",
    "employee_id": "EMP001"
})

# All subsequent enrollments must follow the same structure
# Same keys, same value types (str, int, etc.)
person2_id = str(uuid.uuid4())
db.add_object(person2_id, {
    "first_name": "Bob",
    "last_name": "Jones",
    "employee_id": "EMP002"  # Must be same type (str)
})

# This would fail - different structure (missing key or different type)
# db.add_object(person3_id, {"name": "Charlie"})  # ❌ Wrong keys
```

**Note:** The first attribute added to the database defines its structure. All subsequent attributes must have the same dictionary format - same keys and same value types.

---

### get_id_by_attributes()

Search for object ID by its attributes.

```python
get_id_by_attributes(attributes: Any) -> Optional[str]
```

**Returns:** Object ID or None if not found

**Example:**

```python
# Find person by name
person_id = db.get_id_by_attributes("Alice")
if person_id:
    print(f"Found: {person_id}")
```

---

### get_attributes_by_id()

Get person attributes by object ID.

```python
get_attributes_by_id(object_id: str) -> Optional[Any]
```

**Returns:** Attributes or None if not found

**Example:**

```python
attributes = db.get_attributes_by_id(person_id)
print(f"Person: {attributes}")
```

---

### list_objects()

List all objects in database.

```python
list_objects() -> dict
```

**Returns:** Dictionary mapping object ID to attributes

**Example:**

```python
people = db.list_objects()
for obj_id, attributes in people.items():
    print(f"{attributes}: {obj_id}")
```

---

### remove_object_by_id()

Remove person and all their embeddings and associated images.

```python
remove_object_by_id(object_id: str)
```

**Example:**

```python
db.remove_object_by_id(person_id)
```

---

### remove_object_by_attributes()

Remove person by attributes.

```python
remove_object_by_attributes(attributes: Any)
```

**Example:**

```python
db.remove_object_by_attributes("Alice")
```

---

## Embedding Management

### add_embeddings()

Add face embeddings for a person.

```python
add_embeddings(
    object_id: str,
    embeddings: List[np.ndarray],
    *,
    dedup: bool = True,
    images: Sequence[Union[np.ndarray, bytes]] = ()
) -> int
```

**Parameters:**
- `object_id` (str) - Object ID
- `embeddings` (List[np.ndarray]) - List of embedding vectors
- `dedup` (bool) - Deduplicate embeddings (default: True)
- `images` (Sequence) - Optional face images (numpy arrays or PNG bytes)

**Returns:** Number of embeddings added (after deduplication)

**Example:**

```python
import numpy as np

# Add embeddings without images
embeddings = [np.random.rand(512) for _ in range(5)]
count = db.add_embeddings(person_id, embeddings)
print(f"Added {count} embeddings")

# Add embeddings with images
import cv2
images = [cv2.imread(f"face{i}.jpg") for i in range(3)]
embeddings = [np.random.rand(512) for _ in range(3)]
count = db.add_embeddings(person_id, embeddings, images=images)
```

---

### add_embeddings_for_attributes()

Add embeddings for person attributes (creates person if needed). Object ID will be created automatically as a uuid4 string.

```python
add_embeddings_for_attributes(
    attributes: Any,
    embeddings: List[np.ndarray],
    *,
    dedup: bool = True,
    images: Sequence[Union[np.ndarray, bytes]] = ()
) -> Tuple[int, str]
```

**Returns:** Tuple of (embeddings added, object ID)

**Example:**

```python
# Add embeddings (creates "Bob" if doesn't exist)
count, person_id = db.add_embeddings_for_attributes(
    "Bob",
    embeddings,
    images=images
)
print(f"Added {count} embeddings for {person_id}")
```

---

### get_embeddings()

Get all embeddings and images for a person.

```python
get_embeddings(
    object_id: str,
    *,
    retrieve_images: bool = True
) -> Tuple[List[np.ndarray], List[Optional[np.ndarray]]]
```

**Returns:** Tuple of (embedding vectors, images)

**Example:**

```python
# Get embeddings with images
embeddings, images = db.get_embeddings(person_id)
print(f"Person has {len(embeddings)} embeddings")

for i, (emb, img) in enumerate(zip(embeddings, images)):
    if img is not None:
        cv2.imwrite(f"face_{i}.jpg", img)

# Get embeddings only (faster)
embeddings, _ = db.get_embeddings(person_id, retrieve_images=False)
```

---

### remove_embeddings_by_id()

Remove all embeddings and associated images for a person (keeps person record).

```python
remove_embeddings_by_id(object_id: str)
```

**Example:**

```python
db.remove_embeddings_by_id(person_id)
```

---

### remove_embeddings_by_attributes()

Remove embeddings and associated images by person attributes.

```python
remove_embeddings_by_attributes(attributes: Any)
```

**Example:**

```python
db.remove_embeddings_by_attributes("Alice")
```

---

### count_embeddings()

Count embeddings per person.

```python
count_embeddings() -> Dict[str, Tuple[int, Any]]
```

**Returns:** Dictionary mapping object ID to (count, attributes)

**Example:**

```python
counts = db.count_embeddings()
for obj_id, (count, attributes) in counts.items():
    print(f"{attributes}: {count} embeddings")
```

---

## Search

### get_attributes_by_embedding()

Find person by embedding similarity.

```python
get_attributes_by_embedding(
    embedding: np.ndarray,
    cosine_similarity_threshold: float = 0.6
) -> Tuple[Optional[str], Optional[Any], float]
```

**Returns:** Tuple of (object ID, attributes, similarity score)

**Example:**

```python
# Search for person
query_embedding = np.random.rand(512)
obj_id, attributes, score = db.get_attributes_by_embedding(
    query_embedding,
    cosine_similarity_threshold=0.65
)

if obj_id:
    print(f"Found {attributes} (score: {score:.2f})")
else:
    print("No match found")
```

---

## Database Operations

### backup()

Create zip archive backup of database.

```python
backup(dest: str)
```

**Parameters:**
- `dest` (str) - Destination zip file path

**Example:**

```python
# Backup database
db.backup("./backups/faces_2026-01-04.zip")

# Scheduled backup
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
db.backup(f"./backups/faces_{timestamp}.zip")
```

---

### restore()

Restore database from zip backup.

```python
restore(src: str)
```

**Parameters:**
- `src` (str) - Source zip file path

**Warning:** Replaces current database completely

**Example:**

```python
# Restore from backup
db.restore("./backups/faces_2026-01-04.zip")
```

---

### clear_all_tables()

Delete all data in database.

```python
clear_all_tables()
```

**Warning:** Irreversible - all data is deleted

**Example:**

```python
# Clear test database
db.clear_all_tables()
```

---

## Common Patterns

### Bulk Import

```python
import cv2
import numpy as np

# Import multiple people
people_data = {
    "Alice": ["alice1.jpg", "alice2.jpg", "alice3.jpg"],
    "Bob": ["bob1.jpg", "bob2.jpg"],
    "Carol": ["carol1.jpg", "carol2.jpg", "carol3.jpg"]
}

for name, image_paths in people_data.items():
    images = [cv2.imread(path) for path in image_paths]
    # Get embeddings from your model
    embeddings = [extract_embedding(img) for img in images]
    
    count, person_id = db.add_embeddings_for_attributes(
        name,
        embeddings,
        images=images
    )
    print(f"Added {name}: {count} embeddings")
```

### Database Migration

```python
# Backup old database
old_db = ReID_DatabasePool.get("./old_faces.lance")
old_db.backup("./migration_backup.zip")

# Create new database with new model
new_db = ReID_DatabasePool.get(
    "./new_faces.lance",
    model_name="new_model_v2"
)

# Migrate data (re-extract embeddings with new model)
people = old_db.list_objects()
for obj_id, attributes in people.items():
    old_embeddings, images = old_db.get_embeddings(obj_id)
    
    # Re-extract embeddings with new model
    new_embeddings = [extract_embedding_v2(img) for img in images if img is not None]
    
    new_db.add_embeddings_for_attributes(
        attributes,
        new_embeddings,
        images=[img for img in images if img is not None]
    )
```
