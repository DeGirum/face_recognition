---
description: >-
  DeGirum Face API Reference.
  Centralized logging setup for the face pipelines.
---

{% hint style="info" %}
This API Reference is based on DeGirum Face version 1.4.1.
{% endhint %}



# Functions {#functions}


### configure\_logging\(level='INFO', ...\) {#configure_logging}
`configure_logging(level='INFO', format_str=None, handler=None)`

Configure logging for the degirum\_face package.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `level` | `str` | Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"). | `'INFO'` |
| `format_str` | `Optional[str]` | Custom format string. If None, uses default format. | `None` |
| `handler` | `Optional[Handler]` | Custom handler. If None, uses StreamHandler to stdout. | `None` |

### logging\_disable {#logging_disable}
`logging_disable()`

Disable all logging for the package.

### set\_log\_level\(level\) {#set_log_level}
`set_log_level(level)`

Set the logging level for the package and enable logging.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `level` | `str` | Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"). | *required* |
