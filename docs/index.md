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

`degirum-face` is one of the application packages licensed by DeGirum. Licensing is managed through DeGirum AI Hub. Users need an AI Hub account and a workspace with proper permissions to generate licenses for `degirum-face`. For pricing information, visit the [DeGirum Pricing Page](https://degirum.com/pricing).

The library provides code and pipelines for face recognition workflows. Model licensing is separate from the library licensing:

- **Face detection models**: Trained by DeGirum and can be used commercially when users license the `degirum-face` package
- **Face embedding models**: The ONNX file is from the [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo) and is licensed under the MIT license (see [THIRD-PARTY-LICENSES.md](../THIRD-PARTY-LICENSES.md))

For complete licensing details, see the [Models Reference](reference/models.md).

## Getting Started

Start with [Installation & Setup](getting-started/installation.md) and [Basic Concepts](getting-started/basic-concepts.md), then explore the [Guides](guides/face-recognizer/overview.md) for your use case.

1020
106
168
1282
13
1301
134
1344
1376
1429
143
1457
1519
1555
1559
1662
167
1742
1792
1833
1861
1954
1986
2033
2043
2049
2052
2074
2098
2122
2201
