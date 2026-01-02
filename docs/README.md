# Face Recognition Documentation

Complete documentation for the `degirum_face` face recognition and tracking library.

## Getting Started

- **[Face Recognizer Guide](face_recognizer.md)** - Process individual images and batches
- **[Face Tracker Quick Start](face_tracker_quickstart.md)** - Get started with video tracking quickly

## Face Tracker Documentation

The FaceTracker documentation is split into three guides:

### 1. [Quick Start Guide](face_tracker_quickstart.md)
**Start here!** Get up and running quickly with simple examples.
- Overview and key differences from FaceRecognizer
- When to use FaceTracker vs FaceRecognizer
- Simple webcam monitoring example
- Common use cases with code

### 2. [Configuration Reference](face_tracker_config.md)
Complete reference for all configuration options.
- Video source settings
- Face tracking confirmation
- Alerting and notifications
- Clip storage (S3 and local)
- Live streaming
- ReID expiration filter
- Python and YAML configuration examples

### 3. [Methods Guide](face_tracker_methods.md)
Detailed guide for all FaceTracker methods with workflows.
- Method selection guide (decision tree)
- `start_face_tracking_pipeline()` - Real-time monitoring
- `predict_batch()` - Stream processing with programmatic access
- `find_faces_in_file()` - Analyze local video files
- `find_faces_in_clip()` - Analyze cloud storage clips
- `enroll()` - Add faces to database
- Workflow patterns and examples

## Additional Guides

- **[Face Clip Manager Guide](face_clip_manager.md)** - Manage video clips in object storage

## Quick Navigation

### I want to...

**Monitor a live camera feed for unknown persons**
→ [Quick Start - Security Monitoring](face_tracker_quickstart.md#1-security-monitoring-with-clip-recording)

**Configure alerting and notifications**
→ [Configuration - Alerting](face_tracker_config.md#3-alerting-and-notifications)

**Analyze recorded video footage**
→ [Methods - find_faces_in_file()](face_tracker_methods.md#find_faces_in_file)

**Build a face database from video**
→ [Methods - Workflow Pattern 2](face_tracker_methods.md#pattern-2-batch-processing--enrollment)

**Process video streams programmatically**
→ [Methods - predict_batch()](face_tracker_methods.md#predict_batch)

**Save clips to S3 when alerts trigger**
→ [Configuration - Clip Storage](face_tracker_config.md#4-clip-storage)

**Understand ReID expiration filter**
→ [Configuration - ReID Expiration](face_tracker_config.md#reid-expiration-filter)

---

**Need help?** Start with the [Quick Start Guide](face_tracker_quickstart.md) and work your way through the documentation.
