# Resources

## Community & Support

**DeGirum Community**
Join the [DeGirum Community](https://community.degirum.com) for discussions, questions, and support from the DeGirum team and other users.

**GitHub Issues**
Report bugs or request features at [github.com/DeGirum/face_recognition/issues](https://github.com/DeGirum/face_recognition/issues)

## Examples

Ready-to-run code examples are available in the [DeGirum Face Recognition repository](https://github.com/DeGirum/face_recognition/tree/main/examples):

- **face_recognition_simple.py** - Basic face recognition workflow
- **face_recognition_enroll.py** - Enrolling faces into database
- **face_tracking_simple.py** - Real-time video tracking
- **face_tracking_add_embeddings.py** - Adding embeddings to existing database
- **find_similar_faces.py** - Finding similar faces in database
- **group_similar_faces.py** - Clustering similar faces
- **Tutorials.ipynb** - Interactive Jupyter notebook tutorial

## Troubleshooting

### Common Issues

**Import errors or module not found**
Ensure degirum-face is installed in your active Python environment:
```bash
pip install -i https://pkg.degirum.com degirum-face
```

**Model loading failures**
Verify your hardware platform is correctly specified in the configuration. Check [Hardware Options](getting-started/basic-concepts.md#deployment--hardware) for supported platforms.

**Database connection issues**
Ensure the database path is accessible and you have write permissions. LanceDB creates the database automatically if it doesn't exist.

**Performance issues**
- Use appropriate hardware acceleration when available
- Adjust face quality filters to reduce processing load
- Consider batch processing for large image sets

### Getting Help

1. Check the relevant guide for your component:
   - [Face Recognizer](guides/face-recognizer/overview.md)
   - [Face Tracker](guides/face-tracker/overview.md)
   - [Face Clip Manager](guides/face-clip-manager/overview.md)
   - [Database](guides/database/overview.md)

2. Review [Basic Concepts](getting-started/basic-concepts.md) for terminology and architecture

3. Post your question on the [DeGirum Community](https://community.degirum.com)

4. Report bugs with detailed reproduction steps at [GitHub Issues](https://github.com/DeGirum/face_recognition/issues)
