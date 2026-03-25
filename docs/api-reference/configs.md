---
description: >-
  DeGirum Face API Reference.
  Configuration dataclasses and YAML loaders for recognition and tracking flows.
---

{% hint style="info" %}
This API Reference is based on DeGirum Face version 1.4.1.
{% endhint %}



# Functions {#functions}


### get\_face\_detection\_model\_spec\(device\_type, ...\) {#get_face_detection_model_spec}
`get_face_detection_model_spec(device_type, *, inference_host_address='@cloud', zoo_url=None, token=None)`

Helper function: get face detector model specification

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `device_type` | `str` | The type of device to use. | *required* |
| `inference_host_address` | `str` | The address of the inference host. | `'@cloud'` |
| `zoo_url` | `str` | The URL of the model zoo. | `None` |
| `token` | `str` | The access token for the model zoo. | `None` |

Returns:

| Type | Description |
| --- | --- |
| `ModelSpec` | degirum\_tools.ModelSpec: The model specification for the face detector. |

### get\_face\_embedding\_model\_spec\(device\_type, ...\) {#get_face_embedding_model_spec}
`get_face_embedding_model_spec(device_type, *, inference_host_address='@cloud', zoo_url=None, token=None)`

Helper function: get face embedding model specification

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `device_type` | `str` | The type of device to use. | *required* |
| `inference_host_address` | `str` | The address of the inference host. | `'@cloud'` |
| `zoo_url` | `str` | The URL of the model zoo. | `None` |
| `token` | `str` | The access token for the model zoo. | `None` |

Returns:

| Type | Description |
| --- | --- |
| `ModelSpec` | degirum\_tools.ModelSpec: The model specification for the face re-identification. |

### is\_empty\_storage\_config\(storage\_config\) {#is_empty_storage_config}
`is_empty_storage_config(storage_config)`

Check if the object storage configuration is empty.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `storage_config` | `ObjectStorageConfig` | The object storage configuration. | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `bool` | `bool` | True if the storage configuration is empty, False otherwise. |

# Classes {#classes}


# AlertEvent {#alertevent}
`AlertEvent`

Bases: `str`, `Enum`

Alert event for face search gizmo

# AlertMode {#alertmode}
`AlertMode`

Bases: `Enum`

Alert mode for face search gizmo

# FaceFilterConfig {#facefilterconfig}
`FaceFilterConfig`

`dataclass`

Configuration for face filtering

# FaceRecognizerConfig {#facerecognizerconfig}
`FaceRecognizerConfig`

`dataclass`

Configuration for basic face recognition activities.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `face_detection_model_spec` | `ModelSpec` | Face detection model specification. |
| `face_embedding_model_spec` | `ModelSpec` | Face embedding model specification. |
| `db_path` | `str` | Path to the face re-identification database. |
| `cosine_similarity_threshold` | `float` | Cosine similarity threshold for face matching. |
| `read_consistency_interval` | `Optional[float]` | Time interval in seconds for read consistency in multi-process scenarios. If set, readers will check for updates from writers at this interval. Useful when multiple processes access the same database (e.g., one process enrolling faces while others read for tracking). If None, uses LanceDB default behavior. Typical values: 0.1-1.0 seconds. |
| `face_filters` | `FaceFilterConfig` | Configuration for face filtering. |

## FaceRecognizerConfig Methods {#facerecognizerconfig-methods}

### from\_settings\(settings\) {#from_settings}
`from_settings(settings)`

`staticmethod`

Create FaceRecognizerConfig from settings dictionary.
Args:
settings (dict): Configuration settings as loaded from YAML.

### from\_yaml\(\*, ...\) {#from_yaml}
`from_yaml(*, yaml_file=None, yaml_str=None)`

`classmethod`

Create configuration class instance from YAML configuration.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `yaml_file` | `Optional[str]` | Path to the YAML file. | `None` |
| `yaml_str` | `Optional[str]` | YAML configuration as a string. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `tuple` | `tuple` | (Config object created from YAML, loaded settings dictionary) |

# FaceTrackerConfig {#facetrackerconfig}
`FaceTrackerConfig`

`dataclass`

Bases: `FaceRecognizerConfig`

Configuration for face tracking.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `clip_storage_config` | `ObjectStorageConfig` | Storage configuration for video clips. |
| `credence_count` | `int` | Number of frames to consider a face confirmed. |
| `alert_mode` | `AlertMode` | Alert mode configuration. |
| `alert_once` | `bool` | Whether to trigger the alert only once or each time alert condition happens. |
| `clip_duration` | `int` | Duration of the clip in frames for saving clips. |
| `notification_config` | `str` | Apprise configuration string for notifications. |
| `notification_message` | `str` | Message template for notifications. |
| `notification_timeout_s` | `float` | Timeout in seconds for sending notifications. |
| `video_source` | `Union[int, str]` | Video source; can be integer number to use local camera, RTSP URL, or path to video file. |
| `video_source_fps_override` | `float` | Frame rate override to use when video source reports wrong FPS. |
| `video_source_resolution_override` | `tuple` | Width and height override to use when you need to adjust the video source resolution. |
| `enable_scene_cut_detection` | `bool` | Enable detection of scene cuts in video stream. Useful when processing videos which have multiple scenes or camera switches. |
| `live_stream_mode` | `str` | Live stream mode: "LOCAL", "WEB", or "NONE". |
| `live_stream_rtsp_url` | `str` | RTSP URL path for live stream (if mode is "WEB"). |

## FaceTrackerConfig Methods {#facetrackerconfig-methods}

### default\_clip\_storage\_config {#default_clip_storage_config}
`default_clip_storage_config()`

`staticmethod`

Get default clip storage configuration: disable storage

### from\_settings\(settings\) {#from_settings}
`from_settings(settings)`

`staticmethod`

Create FaceTrackerConfig from settings dictionary.
Args:
settings (dict): Configuration settings as loaded from YAML.
