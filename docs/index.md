# degirum-face Documentation

Complete documentation for the `degirum-face` library - high-performance face recognition and tracking for images and video.

## Getting Started

New to degirum-face? Start here:

- **[Quick Start](getting-started/quickstart.md)** - Your first face recognition in 5 minutes
- **[Basic Concepts](getting-started/basic-concepts.md)** - Core concepts and terminology

## User Guides

### Face Recognition (Images & Batches)

Process individual images or batches without temporal tracking:

- **[Overview](guides/face-recognizer/overview.md)** - When to use FaceRecognizer and key concepts
- **[Configuration](guides/face-recognizer/configuration.md)** - Configure models, hardware, and filters
- **[Methods & API](guides/face-recognizer/methods.md)** - enroll, predict, and batch processing

### Face Tracking (Video & Streams)

Real-time video surveillance with persistent tracking:

- **[Quick Start](guides/face-tracker/quickstart.md)** - Get started with video tracking
- **[Configuration](guides/face-tracker/configuration.md)** - Video sources, alerting, and clip storage
- **[Methods & Workflows](guides/face-tracker/methods.md)** - All methods with use cases
- **[Clip Manager](guides/face-clip-manager.md)** - Manage video clips in storage

## Reference

- **[Face Filters](reference/face-filters.md)** - Quality gates and filtering options
- **[YAML Configuration](reference/yaml-config.md)** - YAML configuration reference
- **[Hardware Support](reference/hardware.md)** - Supported accelerators and platforms

## Quick Navigation

### I want to...

**Recognize faces in photos**
→ [Face Recognizer Quick Start](guides/face-recognizer/overview.md#quick-example)

**Monitor a live camera feed**
→ [Face Tracker Quick Start](guides/face-tracker/quickstart.md)

**Process a batch of images**
→ [Batch Processing Guide](guides/face-recognizer/methods.md#predict_batch---recognize-faces-in-multiple-images-or-video-streams)

**Deploy to edge hardware (Hailo, Intel NPU)**
→ [Hardware Options](getting-started/basic-concepts.md#deployment--hardware)

**Configure face quality filters**
→ [Face Filters Reference](reference/face-filters.md)

**Save alert clips to S3**
→ [Clip Storage Configuration](guides/face-tracker/configuration.md#4-clip-storage)

**Use YAML configuration files**
→ [YAML Configuration](reference/yaml-config.md)

---

## Examples

See the [examples/](../examples/) directory for ready-to-run code samples.

## Support

- **GitHub Issues:** [Report bugs or request features](https://github.com/DeGirum/degirum_face/issues)
- **Documentation:** You're reading it!
- **Examples:** Check [examples/](../examples/) directory
