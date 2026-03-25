---
description: >-
  DeGirum Face API Reference.
  Pipeline orchestration for enrollment, recognition, and alert handling.
---

{% hint style="info" %}
This API Reference is based on DeGirum Face version 1.4.1.
{% endhint %}



# Functions {#functions}


# Classes {#classes}


# FaceClipManager {#faceclipmanager}
`FaceClipManager`

Class to annotate and manage video clips in the object storage.

## FaceClipManager Methods {#faceclipmanager-methods}

### \_\_init\_\_\(storage\_config\) {#\_\_init\_\_}
`__init__(storage_config)`

Constructor.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `storage_config` | `ObjectStorageConfig` | Configuration for face clip management. | *required* |

### download\_file\(filename\) {#download_file}
`download_file(filename)`

Download the file object from the storage.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `filename` | `str` | The name of the file to download. | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `bytes` | `bytes` | The bytes of the downloaded file. |

### list\_clips {#list_clips}
`list_clips()`

List the video clips in the storage.
Returns a dictionary where the key is the clip filename and value is the dict of
video clip file objects (of minio.datatypes.Object type) associated with that clip
original video clip: "original" key,
JSON annotations: "json" key,
annotated video clip: "annotated" key

### remove\_all\_clips {#remove_all_clips}
`remove_all_clips()`

Remove all clip-related file objects from the storage.

### remove\_file\(filename\) {#remove_file}
`remove_file(filename)`

Remove the file object from the storage.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `filename` | `str` | The name of the file to remove. | *required* |

# FaceRecognizer {#facerecognizer}
`FaceRecognizer`

Face recognition class for processing images and recognizing faces.
Provides basic face recognition capabilities: face recognition and face enrolling.

## FaceRecognizer Methods {#facerecognizer-methods}

### \_\_init\_\_\(config=FaceRecognizerConfig\(\)\) {#\_\_init\_\_}
`__init__(config=FaceRecognizerConfig())`

Constructor.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `FaceRecognizerConfig` | Configuration for face recognition. | `FaceRecognizerConfig()` |

### enroll\_batch\(frames, ...\) {#enroll_batch}
`enroll_batch(frames, attributes)`

Enroll a batch of frames for face recognition.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `frames` | `Iterable` | An iterator yielding frames as numpy arrays or file paths | *required* |
| `attributes` | `Iterable` | An iterator yielding attributes for each frame | *required* |

Returns:

| Type | Description |
| --- | --- |
| `List[FaceRecognitionResult]` | List[FaceRecognitionResult]: A list of face recognition results for each enrolled face. |
| `List[FaceRecognitionResult]` | If for some frame no face was found, that frame is skipped and not included in the results list. |

### enroll\_image\(frame, ...\) {#enroll_image}
`enroll_image(frame, attributes)`

Enroll a single image for face recognition.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `frame` | `Any` | The input image frame as a numpy array or file path. | *required* |
| `attributes` | `Any` | The attributes for the image (e.g., person name). | *required* |

Returns:

| Type | Description |
| --- | --- |
| `Optional[FaceRecognitionResult]` | Optional[FaceRecognitionResult]: The face recognition result for the enrolled image, or None if enrollment failed. |

### predict\(frame\) {#predict}
`predict(frame)`

Recognize faces in a single image.

Note: Use this method for single image recognitions only where throughput is not a concern.
For efficient pipelined batch processing, use `predict_batch()`.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `frame` | `Any` | The input frame to recognize. | *required* |

Returns:

| Type | Description |
| --- | --- |
| [InferenceResults](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor#degirum.postprocessor.inferenceresults) | dg.postprocessor.[InferenceResults](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor#degirum.postprocessor.inferenceresults): The face detection inference results |
| [InferenceResults](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor#degirum.postprocessor.inferenceresults) | augmented with face recognition results. See `predict_batch()` for more details. |

### predict\_batch\(frames\) {#predict_batch}
`predict_batch(frames)`

Recognize faces in a batch of frames.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `frames` | `Iterable` | An iterator yielding frames as numpy arrays or file paths | *required* |

Returns:

| Type | Description |
| --- | --- |
| `Iterator[InferenceResults]` | An iterator yielding face detection inference results provided by face detection model |
| `Iterator[InferenceResults]` | augmented with face recognition results. For each detected object the following key are |
| `Iterator[InferenceResults]` | added to the object dictionary: "face\_embeddings": face embedding vector "face\_db\_id": database ID string of recognized face "face\_attributes": recognized face attributes (usually person name string) "face\_similarity\_score": face similarity score from the database search "frame\_id": input frame ID "face\_properties": additional face properties such as gender, age, emotion, etc. "face\_crop\_img": the cropped face image |
| `Iterator[InferenceResults]` | Also `faces` property is added to of the returned [InferenceResults](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor#degirum.postprocessor.inferenceresults) object. |
| `Iterator[InferenceResults]` | It is a list of FaceRecognitionResult objects corresponding to each detected face. |

# FaceTracker {#facetracker}
`FaceTracker`

Class to run face tracking pipeline on streaming video source.

## FaceTracker Methods {#facetracker-methods}

### \_\_init\_\_\(config=FaceTrackerConfig\(\)\) {#\_\_init\_\_}
`__init__(config=FaceTrackerConfig())`

Constructor.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `FaceTrackerConfig` | Configuration for face tracking. | `FaceTrackerConfig()` |

### enroll\(face\_list\) {#enroll}
`enroll(face_list)`

Enroll a list of face attributes into the database.
You obtain this list by running find\_faces\_in\_clip/find\_faces\_in\_file methods and taking .values() of the returned dict.
Then you need to assign attributes (e.g., person name) to each face object in the list
before calling this method.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `face_list` | `Union[FaceAttributes, List[FaceAttributes]]` | The face attributes object or list of face attributes to enroll. | *required* |

### find\_faces\_in\_clip\(clip\_object\_name, ...\) {#find_faces_in_clip}
`find_faces_in_clip(clip_object_name, *, save_annotated=True, compute_clusters=True)`

Run the face analysis and annotation pipeline on a video clip object.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `clip_object_name` | `str` | The video clip file object name in object storage. | *required* |
| `save_annotated` | `bool` | Whether to save the annotated video clip to the object storage. | `True` |
| `compute_clusters` | `bool` | Whether to compute K-means clustering on the embeddings. | `True` |

Returns:

| Type | Description |
| --- | --- |
| `Dict[int, FaceStatus]` | Dict[int, FaceStatus]: The dictionary of face track IDs to face objects found in the clip. Each face object includes a table of embeddings and attributes (if recognized). |

### find\_faces\_in\_file\(file\_path, ...\) {#find_faces_in_file}
`find_faces_in_file(file_path, *, save_annotated=True, output_video_path=None, compute_clusters=True)`

Run the face analysis and annotation pipeline on a video clip local file.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file_path` | `str` | The video clip file path | *required* |
| `save_annotated` | `bool` | Whether to save the annotated video clip to a file. | `True` |
| `output_video_path` | `str` | The file path to save the annotated video clip into. | `None` |
| `compute_clusters` | `bool` | Whether to compute K-means clustering on the embeddings. | `True` |

Returns:

| Type | Description |
| --- | --- |
| `Dict[int, FaceStatus]` | Dict[int, FaceStatus]: The dictionary of face track IDs to face objects found in the clip. Each face object includes a table of embeddings and attributes (if recognized). |

### predict\_batch\(stream\) {#predict_batch}
`predict_batch(stream)`

Recognize faces in a video stream.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `stream` | `Iterable` | An iterator yielding video frames as numpy arrays | *required* |

Returns:

| Type | Description |
| --- | --- |
| `Iterator[InferenceResults]` | An iterator yielding face detection inference results provided by face detection model |
| `Iterator[InferenceResults]` | augmented with face recognition results. For each detected object the following key are |
| `Iterator[InferenceResults]` | added to the object dictionary: "face\_embeddings": face embedding vector "face\_db\_id": database ID string of recognized face "face\_attributes": recognized face attributes (usually person name string) "face\_similarity\_score": face similarity score from the database search "frame\_id": input frame ID "face\_properties": additional face properties such as gender, age, emotion, etc. "face\_crop\_img": the cropped face image |
| `Iterator[InferenceResults]` | Also `faces` property is added to of the returned [InferenceResults](https://docs.degirum.com/pysdk/user-guide-pysdk/api-ref/postprocessor#degirum.postprocessor.inferenceresults) object. |
| `Iterator[InferenceResults]` | It is a list of FaceRecognitionResult objects corresponding to each detected face. |

### start\_face\_tracking\_pipeline\(\*, ...\) {#start_face_tracking_pipeline}
`start_face_tracking_pipeline(*, frame_iterator=None, sink=None, sink_connection_point='detector')`

Run the face tracking pipeline on streaming video source.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `frame_iterator` | `Optional[Iterable]` | Optional iterator yielding frames as numpy arrays or file paths. If specified, substitutes the video source defined in the config. | `None` |
| `sink` | `Optional[SinkGizmo]` | Optional sink gizmo to direct the output to. | `None` |
| `sink_connection_point` | `str` | The connection point in the pipeline to attach the sink gizmo. Possible values are "detector" (after face detector) or "recognizer" (after face recognizer). | `'detector'` |

Returns:
tuple: A tuple containing:
- Composition: The pipeline composition object.
- Watchdog: Watchdog object to monitor the pipeline.
