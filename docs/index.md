# Introduction

**degirum-face** is a high-performance Python library for face detection, recognition, and tracking in images and video. Built for production deployments with minimal code and support for CPU and edge AI accelerators. Code examples and usage tutorials are available in the [DeGirum Face Recognition repo](https://github.com/DeGirum/face_recognition).

**Fast and efficient** face recognition with:
- Face detection, alignment, embedding extraction, and matching for images, video files, and live streams
- **Multi-hardware support**: CPU, GPU, and edge AI accelerators (Hailo, Axelera, DEEPX, Intel, NVIDIA, Rockchip, Google, DeGirum)
- **Simple APIs**: Minimal code to detect, enroll, and recognize faces with easy batch processing
- **Flexible configuration**: Python or YAML config for models, thresholds, and database paths
- **Production-ready tracking**: Real-time face re-identification, event notifications, and automated alert recording
- **Robust database**: LanceDB-based storage with vector similarity search

## Licensing

`degirum-face` is one of the application packages licensed by DeGirum. Licensing is managed through [DeGirum AI Hub](https://hub.degirum.com/). Users need to create an AI Hub account and set up a workspace with the appropriate permissions to generate licenses for `degirum-face`. For workspace plan details and pricing information, visit the [Workspace Plans](https://docs.degirum.com/ai-hub/workspace-plans) page and the [DeGirum Pricing Page](https://degirum.com/pricing).

The library provides code and pipelines for face recognition workflows. Model licensing is separate from the library licensing:

- **Face detection models**: Trained by DeGirum and can be used commercially when users license the `degirum-face` package
- **Face embedding models**: The ONNX file is from the [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo) and is licensed under the MIT license (see [THIRD-PARTY-LICENSES.md](../THIRD-PARTY-LICENSES.md))

For complete licensing details, see the [Models Reference](reference/models.md).

## Getting Started

Start with [Installation & Setup](getting-started/installation.md) and [Basic Concepts](getting-started/basic-concepts.md), then explore the [Guides](guides/face-recognizer/overview.md) for your use case.


