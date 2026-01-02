#
# face_tracking_add_embeddings: Face Tracking Example How to Add Embeddings to Database
#
# Copyright DeGirum Corporation 2025
# All rights reserved
#
# Implements analysis of provided video clip: face detection, embeddings computation, and
# adding embeddings to the ReID database.
# This example assumes that provided video clip contains exactly one person.
#
# Usage: `python face_tracking_add_embeddings.py <video_clip> <person_name>`
#
# When you run this example without arguments, it will list available video clips in the object storage
# and known persons in the database. <video_clip> should be among the listed video clips.
#
# You can configure all the settings in the `face_tracking.yaml` file.
#
# Pre-requisites:
# - Install DeGirum Face SDK: `pip install degirum-face`
# - Run `face_tracking_simple.py` examples to collect video clips of unknown persons
#


import degirum_face, sys, os


def main():
    # load settings from YAML file
    config, _ = degirum_face.FaceTrackerConfig.from_yaml(yaml_file="face_tracking.yaml")

    # create clip manager instance
    clip_manager = degirum_face.FaceClipManager(config.clip_storage_config)

    # create face tracker instance
    face_tracker = degirum_face.FaceTracker(config)

    # check command line arguments
    if len(sys.argv) != 3:
        print(f"Usage: python {os.path.basename(__file__)} <clip_name> <person_name>")
        print("\nAvailable video clips in storage:")
        for clip_info in clip_manager.list_clips().values():
            if "original" in clip_info:
                print(f"  {clip_info['original'].object_name}")
        print("Person names currently in database:")
        for person in face_tracker.db.list_objects().values():
            print(f"  {person}")
        sys.exit(1)

    video_file = sys.argv[1]
    person_name = sys.argv[2]

    # run analysis pipeline on the video file
    print(f"Processing video file: {video_file}")
    face_map = face_tracker.find_faces_in_clip(video_file, save_annotated=False)

    if len(face_map) != 1:
        print(
            f"Error: {len(face_map)} faces detected. This example assumes exactly one person."
        )
        sys.exit(1)

    # add embeddings to the database
    for face_obj in face_map.values():
        face_obj.attributes = person_name
        face_tracker.enroll(face_obj)

    # print database contents
    print(
        f"{person_name} is enrolled.\n\nPersons currently in database:\n{face_tracker.db.count_embeddings()}"
    )


if __name__ == "__main__":
    main()
