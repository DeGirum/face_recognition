---
description: >-
  DeGirum Face API Reference.
  Shared math, filtering, and post-processing helpers.
---

{% hint style="info" %}
This API Reference is based on DeGirum Face version 1.4.1.
{% endhint %}



# Functions {#functions}


### face\_align\_and\_crop\(img, ...\) {#face_align_and_crop}
`face_align_and_crop(img, landmarks, image_size)`

Align and crop the face from the image based on the given landmarks.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `img` | `ndarray` | The full image (not the cropped bounding box). | *required* |
| `landmarks` | `List[ndarray]` | List of 5 keypoints (landmarks) as (x, y) coordinates in the following order: [left eye, right eye, nose, left mouth, right mouth]. | *required* |
| `image_size` | `int` | The size to which the image should be resized. | *required* |

Returns:

| Type | Description |
| --- | --- |
| `ndarray` | np.ndarray: the aligned face image |

### face\_is\_frontal\(landmarks\) {#face_is_frontal}
`face_is_frontal(landmarks)`

Check if the face is frontal based on the landmarks.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `landmarks` | `List[ndarray]` | List of 5 keypoints (landmarks) as (x, y) coordinates in the following order: [left eye, right eye, nose, left mouth, right mouth]. | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `bool` | `bool` | True if the face is frontal, False otherwise. |

### face\_is\_shifted\(bbox, ...\) {#face_is_shifted}
`face_is_shifted(bbox, landmarks)`

Check if the face is shifted based on the landmarks.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `bbox` | `List[float]` | Bounding box of the face as [x1, y1, x2, y2]. | *required* |
| `landmarks` | `List[ndarray]` | List of keypoints (landmarks) as (x, y) coordinates | *required* |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `bool` | `bool` | True if the face is shifted to a side of bbox, False otherwise. |
