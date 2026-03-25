---
description: >-
  DeGirum Face API Reference.
  Re-identification database APIs backed by LanceDB.
---

{% hint style="info" %}
This API Reference is based on DeGirum Face version 1.4.1.
{% endhint %}



# Classes {#classes}


# ReID\_Database {#reid_database}
`ReID_Database`

Class to hold the database of object embeddings.

## ReID\_Database Methods {#reid-_database-methods}

### \_\_init\_\_\(db\_path, ...\) {#\_\_init\_\_}
`__init__(db_path, model_name=None, read_consistency_interval=None)`

Constructor.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `db_path` | `str` | Path to the database file. | *required* |
| `model_name` | `Optional[str]` | Name of the embedding model. If provided and database exists, validates that it matches the stored model name. | `None` |
| `read_consistency_interval` | `Optional[float]` | Time interval in seconds for read consistency in multi-process scenarios. If set, readers will check for updates from writers at this interval. Useful when multiple processes access the same database (e.g., one process enrolling faces while others read for tracking). If None, uses LanceDB default behavior. Typical values: 0.1-1.0 seconds. | `None` |

Raises:

| Type | Description |
| --- | --- |
| `ValueError` | If model\_name doesn't match the existing database's model name. |

### add\_embeddings\(object\_id, ...\) {#add_embeddings}
`add_embeddings(object_id, embeddings, *, dedup=True, images=())`

Add an embedding for given object ID to the database.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `object_id` | `str` | The object ID. | *required* |
| `embeddings` | `List[ndarray]` | The list of embedding vectors. | *required* |
| `dedup` | `bool` | Whether to deduplicate embeddings. If True, only unique embeddings will be added. | `True` |
| `images` | `Sequence[Union[ndarray, bytes]]` | Optional sequence of images to associate with embeddings. Each image corresponds to the embedding at the same index. If numpy array, it will be converted to PNG. If bytes, it's treated as PNG blob. Sequence can be empty. | `()` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `int` | `int` | The number of embeddings added to the database (can be smaller than the input list if dedup is enabled). |

### add\_embeddings\_for\_attributes\(attributes, ...\) {#add_embeddings_for_attributes}
`add_embeddings_for_attributes(attributes, embeddings, *, dedup=True, images=())`

Add embeddings for a specific person's attributes.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `attributes` | `Any` | The attributes of the object. If no object ID is found, a new one will be created. | *required* |
| `embeddings` | `List[ndarray]` | The list of embedding vectors. | *required* |
| `dedup` | `bool` | Whether to deduplicate embeddings. If True, only unique embeddings will be added. | `True` |
| `images` | `Sequence[Union[ndarray, bytes]]` | Optional sequence of images to associate with embeddings. Each image corresponds to the embedding at the same index. If numpy array, it will be converted to PNG. If bytes, it's treated as PNG blob. Sequence can be empty. | `()` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `tuple` | `Tuple[int, str]` | The tuple containing the number of embeddings added and the corresponding object ID. |

### add\_object\(object\_id, ...\) {#add_object}
`add_object(object_id, attributes)`

Add or change object attributes in the object attributes table.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `object_id` | `str` | The unique object ID. | *required* |
| `attributes` | `Any` | The attributes of the object to add/change | *required* |

### backup\(dest\) {#backup}
`backup(dest)`

Create a zip archive backup of the entire database directory.

This method creates a complete backup of all database files by:
1. Closing all open table handles to ensure data is flushed to disk
2. Creating a zip archive of the entire database directory
3. Reconnecting to the database after backup is complete

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `dest` | `str` | Full path to the destination zip file (e.g., "/path/to/backup.zip") | *required* |

Raises:

| Type | Description |
| --- | --- |
| `FileNotFoundError` | If the database directory does not exist |
| `IOError` | If there are issues creating the zip archive |

### clear\_all\_tables {#clear_all_tables}
`clear_all_tables()`

Clear all data in the database.
This method drops all tables in the database and clears the internal table cache.

### count\_embeddings {#count_embeddings}
`count_embeddings()`

Count all object embeddings in the database.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `dict` | `Dict[str, Tuple[int, Any]]` | A dictionary where the key is the object ID and the value is the tuple containing count of embeddings for that object and its attributes. |

### get\_attributes\_by\_embedding\(embedding, ...\) {#get_attributes_by_embedding}
`get_attributes_by_embedding(embedding, cosine_similarity_threshold=0.6)`

Get the object ID and its attributes by its embedding.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `embedding` | `ndarray` | The embedding vector. | *required* |
| `cosine_similarity_threshold` | `float` | Threshold for the cosine similarity metric. | `0.6` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `tuple` | `Tuple[Optional[str], Optional[Any], float]` | The tuple containing object ID, object attributes, and similarity score; (None, None, 0.0) if not found. |

### get\_attributes\_by\_id\(object\_id\) {#get_attributes_by_id}
`get_attributes_by_id(object_id)`

Get object attributes by object ID

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `object_id` | `str` | Object ID string. | *required* |

Returns:

| Type | Description |
| --- | --- |
| `Optional[Any]` | Optional[Any]: The attributes of the object or None if not found. |

### get\_embeddings\(object\_id, ...\) {#get_embeddings}
`get_embeddings(object_id, *, retrieve_images=True)`

Get all embeddings and associated images for a given object ID.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `object_id` | `str` | The object ID. | *required* |
| `retrieve_images` | `bool` | Whether to retrieve associated images. If False, images will be returned as []. | `True` |

Returns:

| Type | Description |
| --- | --- |
| `Tuple[List[ndarray], List[Optional[ndarray]]]` | Tuple[List[np.ndarray], List[Optional[np.ndarray]]]: A tuple containing: - List of embedding vectors - List of corresponding images if retrieve\_images is True (any element can be None if there is no image associated with corresponding embedding) |

### get\_id\_by\_attributes\(attributes\) {#get_id_by_attributes}
`get_id_by_attributes(attributes)`

Get object ID by its attributes.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `attributes` | `Any` | The attributes of the object. | *required* |

Returns:

| Type | Description |
| --- | --- |
| `Optional[str]` | Optional[str]: The object ID or None if not found. |

### list\_objects {#list_objects}
`list_objects()`

List all object IDs in the database.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `dict` | `dict` | map of object ID to attributes |

### remove\_embeddings\_by\_attributes\(attributes\) {#remove_embeddings_by_attributes}
`remove_embeddings_by_attributes(attributes)`

Remove all embeddings for a given object's attributes.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `attributes` | `Any` | The attributes of the object. | *required* |

### remove\_embeddings\_by\_id\(object\_id\) {#remove_embeddings_by_id}
`remove_embeddings_by_id(object_id)`

Remove all embeddings and associated images for a given object ID.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `object_id` | `str` | The object ID. | *required* |

### remove\_object\_by\_attributes\(attributes\) {#remove_object_by_attributes}
`remove_object_by_attributes(attributes)`

Remove object and its embeddings from the database by attributes.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `attributes` | `Any` | The attributes of the object. | *required* |

### remove\_object\_by\_id\(object\_id\) {#remove_object_by_id}
`remove_object_by_id(object_id)`

Remove object and its embeddings from the database.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `object_id` | `str` | The object ID. | *required* |

### restore\(src\) {#restore}
`restore(src)`

Restore database from a zip archive backup.

This method restores the database by:
1. Closing all open table handles
2. Removing the existing database directory
3. Extracting the backup archive to restore all database files
4. Reconnecting to the restored database

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `src` | `str` | Full path to the source zip file (e.g., "/path/to/backup.zip") | *required* |

Raises:

| Type | Description |
| --- | --- |
| `FileNotFoundError` | If the backup zip file does not exist |
| `IOError` | If there are issues extracting the archive |

# ReID\_DatabasePool {#reid_databasepool}
`ReID_DatabasePool`

Pool manager for ReID\_Database instances.
Ensures only one database connection exists per unique database path.

## ReID\_DatabasePool Methods {#reid-_databasepool-methods}

### get\(db\_path, ...\) {#get}
`get(db_path, model_name=None, read_consistency_interval=None)`

`staticmethod`

Get or create a ReID\_Database instance for the given database path.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `db_path` | `str` | Path to the database file. | *required* |
| `model_name` | `Optional[str]` | Name of the embedding model. If provided and database exists, validates that it matches the stored model name. | `None` |
| `read_consistency_interval` | `Optional[float]` | Time interval in seconds for read consistency in multi-process scenarios. If set, readers will check for updates from writers at this interval. Only used when creating a new database instance. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `ReID_Database` | `ReID_Database` | The database instance for the given path. |

Raises:

| Type | Description |
| --- | --- |
| `ValueError` | If model\_name doesn't match the existing database's model name. |
