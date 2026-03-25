---
description: >-
  DeGirum Face API Reference.
  Face metadata utilities plus LanceDB record structures.
---

{% hint style="info" %}
This API Reference is based on DeGirum Face version 1.4.1.
{% endhint %}



# Classes {#classes}


# FaceAttributes {#faceattributes}
`FaceAttributes`

`dataclass`

Class to hold detected face attributes

## FaceAttributes Methods {#faceattributes-methods}

### from\_subclass\(obj\) {#from_subclass}
`from_subclass(obj)`

`staticmethod`

Create FaceAttributes instance from a subclass object (e.g., FaceStatus or FaceRecognitionResult).

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `obj` | `FaceAttributes` | Instance of FaceAttributes or any subclass | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `FaceAttributes` | `FaceAttributes` | New instance with only base class attributes |

# FaceMap {#facemap}
`FaceMap`

Thread-safe map of object IDs to object attributes.

## FaceMap Methods {#facemap-methods}

### \_\_enter\_\_ {#\_\_enter\_\_}
`__enter__()`

Context manager entry: acquire the lock.

Returns:

| Type | Description |
| --- | --- |
|  | Dict[int, Any]: Direct reference to the internal map (use with caution while lock is held). |

### \_\_exit\_\_\(exc\_type, ...\) {#\_\_exit\_\_}
`__exit__(exc_type, exc_val, exc_tb)`

Context manager exit: release the lock.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `exc_type` |  | Exception type if an exception occurred. | *required* |
| `exc_val` |  | Exception value if an exception occurred. | *required* |
| `exc_tb` |  | Exception traceback if an exception occurred. | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `bool` |  | False to propagate exceptions. |

### \_\_init\_\_ {#\_\_init\_\_}
`__init__()`

Constructor.

### \_\_len\_\_ {#\_\_len\_\_}
`__len__()`

Get the number of items in the map.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `int` | `int` | Number of items in the map. |

### delete\(expr\) {#delete}
`delete(expr)`

Delete objects from the map

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `expr` | `lambda` | logical expression to filter objects to delete | *required* |

Returns:

| Type | Description |
| --- | --- |
| `Dict[int, Any]` | Dict[int, Any]: Map of deleted object IDs to their values. |

### get\(id\) {#get}
`get(id)`

Get the object by ID

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `id` | `int` | The ID of the tracked face. | *required* |

Returns:

| Type | Description |
| --- | --- |
| `Optional[Any]` | Optional[Any]: The deep copy of object attributes or None if not found. |

### items {#items}
`items()`

Get an iterator over all items in the map.

Note: This method should be called within a 'with face\_map:' context to ensure thread safety.

Returns:

| Type | Description |
| --- | --- |
|  | Iterator of (id, face) tuples. |

### put\(id, ...\) {#put}
`put(id, value)`

Add/update an object in the map

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `id` | `int` | Object ID | *required* |
| `value` | `Any` | Object attributes reference | *required* |

### read\_alerts {#read_alerts}
`read_alerts()`

Read the alerts and reset them.

Returns:

| Type | Description |
| --- | --- |
| `Dict[str, list]` | Dict[str, list]: The map of alert messages if triggered, empty map otherwise. |

### set\_alert\(alert, ...\) {#set_alert}
`set_alert(alert, info)`

Set the alert message.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `alert` | `str` | The alert ID to set. | *required* |
| `info` | `Any` | Additional information related to the alert. | *required* |

# FaceOptionalProperties {#faceoptionalproperties}
`FaceOptionalProperties`

`dataclass`

Class to hold detected face optional properties (model-dependent)

## FaceOptionalProperties Methods {#faceoptionalproperties-methods}

### from\_dict\(result\) {#from_dict}
`from_dict(result)`

`staticmethod`

Create FaceOptionalProperties instance from face embedding result dictionary

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `result` | `Dict[str, Any]` | Dictionary containing face embedding results as returned by face embedding model | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `FaceOptionalProperties` | `FaceOptionalProperties` | New instance initialized from result data |

# FaceRecognitionResult {#facerecognitionresult}
`FaceRecognitionResult`

`dataclass`

Bases: `FaceAttributes`

Class to hold face recognition results

## FaceRecognitionResult Methods {#facerecognitionresult-methods}

### \_\_str\_\_ {#\_\_str\_\_}
`__str__()`

Pretty print the face recognition results.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Formatted string representation of the results |

### from\_dict\(result\) {#from_dict}
`from_dict(result)`

`staticmethod`

Create FaceRecognitionResult instance from object detection result dictionary augmented with face recognition data.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `result` | `Dict[str, Any]` | Dictionary containing face detection/recognition results as returned by face recognition pipeline | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `FaceRecognitionResult` | `FaceRecognitionResult` | New instance initialized from result data |

# FaceStatus {#facestatus}
`FaceStatus`

`dataclass`

Bases: `FaceAttributes`

Class to hold detected face runtime status.
