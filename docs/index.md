# Introduction

**degirum-face** is a high-performance Python library for face detection, recognition, and tracking in images and video. Built for production deployments with minimal code and support for CPU and edge AI accelerators.

**Fast and efficient** face recognition with:
- Face detection, alignment, embedding extraction, and matching for images, video files, and live streams
- **Multi-hardware support**: CPU, GPU, and edge AI accelerators (Hailo, Axelera, DEEPX, Intel, NVIDIA, Rockchip, Google, DeGirum)
- **Simple APIs**: Minimal code to detect, enroll, and recognize faces with easy batch processing
- **Flexible configuration**: Python or YAML config for models, thresholds, and database paths
- **Production-ready tracking**: Real-time face re-identification, event notifications, and automated alert recording
- **Robust database**: LanceDB-based storage with vector similarity search

## Licensing

`degirum-face` is part of the application packages licensed by DeGirum. The library provides code and pipelines for face recognition workflows. Model licensing is separate from the library licensing:

- **Face detection models**: Licenses are included in `degirum_face` licensing
- **Face embedding models**: Currently available models in the registry require contacting Hailo for licensing

Licensing is managed through DeGirum AI Hub. Users need an AI Hub account and a workspace with proper permissions to generate licenses for `degirum-face`. For pricing information, visit the [DeGirum Pricing Page](https://degirum.com/pricing).

For complete licensing details, see the [Models Reference](reference/models.md).

## Getting Started

Start with [Installation & Setup](getting-started/installation.md) and [Basic Concepts](getting-started/basic-concepts.md), then explore the [Guides](guides/face-recognizer/overview.md) for your use case.
