---
description: >-
  DeGirum Face API Reference.
  Hardware discovery helpers built on the embedded model registry.
---

{% hint style="info" %}
This API Reference is based on DeGirum Face version 1.4.1.
{% endhint %}



Discovery functions for the degirum\_face package

This module provides functions to discover:
1. Available hardware on different inference hosts
2. Compatible hardware (intersection of registry and system)
3. Compatible models based on hardware/task filters

Note: For registry hardware/tasks, use degirum\_face.model\_registry.get\_hardware()
and degirum\_face.model\_registry.get\_tasks() directly.

# Functions {#functions}


### get\_compatible\_hw\(inference\_host\_address='@local'\) {#get_compatible_hw}
`get_compatible_hw(inference_host_address='@local')`

Get hardware types that are both in the registry AND available on the system

This is the most useful function for users - it shows what hardware they can actually use.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `inference_host_address` | `str` | Where to check for hardware - "@local": Local system using 'degirum sys-info' - "@cloud": DeGirum cloud using degirum.get\_supported\_devices() - "host\_ip": AI server using 'degirum sys-info --host host\_ip' | `'@local'` |

Returns:

| Type | Description |
| --- | --- |
| `List[str]` | List[str]: List of hardware types that work on both registry and system |

### get\_system\_hw\(inference\_host\_address='@local'\) {#get_system_hw}
`get_system_hw(inference_host_address='@local')`

Get hardware available on a specific inference host

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `inference_host_address` | `str` | Where to check for hardware - "@local": Local system using degirum.get\_supported\_devices() - "@cloud": DeGirum cloud using degirum.get\_supported\_devices() - "host\_ip": AI server using degirum.get\_supported\_devices() | `'@local'` |

Returns:

| Type | Description |
| --- | --- |
| `List[str]` | List[str]: List of available hardware types (e.g., ['HAILORT/HAILO8', 'TFLITE/CPU']) Returns empty list if detection fails |
