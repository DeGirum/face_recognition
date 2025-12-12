#
# face_tracking_web_app.py: Face Tracking Example Web Application
#
# Copyright DeGirum Corporation 2025
# All rights reserved
#
# Implements NiceGUI web application for face tracking using DeGirum's face recognition package.
# Provides a live stream of the camera feed, allows video clip annotation, and manages face reID database.
# You can configure all the settings in the `config.yaml` file.
#
# Pre-requisites:
# - Install NiceGUI: `pip install nicegui`
# - Install DeGirum Face SDK: `pip install degirum-face`
#

import os, io, asyncio, urllib.parse, uuid

import degirum_face
from degirum_tools import MediaServer

from typing import List
from nicegui import ui, app, context
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi import Request


#
# Global variables
#

# media server instance for RTSP streaming
media_server: MediaServer = None  # type: ignore

# configuration of face tracking pipeline
config: degirum_face.FaceTrackerConfig = None  # type: ignore

# clip manager instance for annotating video clips
clip_manager: degirum_face.FaceClipManager = None  # type: ignore

# list of pipelines running face tracking and their watchdogs
pipelines: List[tuple] = []


@app.on_startup
def startup():
    """Initialize the face tracking application on startup."""

    # load settings from YAML file
    global config
    config, _ = degirum_face.FaceTrackerConfig.from_yaml(yaml_file="config.yaml")
    config.live_stream_mode = "WEB"

    # create FaceTracker instance
    face_tracker = degirum_face.FaceTracker(config)

    # start face tracking pipeline
    pipelines.append(face_tracker.start_face_tracking_pipeline())

    # create clip manager
    global clip_manager
    clip_manager = degirum_face.FaceClipManager(config)

    # start media server for RTSP streaming
    global media_server
    media_server = MediaServer()


@app.on_shutdown
def cleanup():
    """Cleanup function to stop the media server and pipelines."""

    for composition, _ in pipelines:
        composition.stop()

    media_server.stop()  # stop the media server


@ui.page("/health")
def health_check():
    """Health check endpoint."""

    if not pipelines:
        return JSONResponse(status_code=500, content={"status": "No pipelines running"})

    status = "ok"
    pipeline_states = []
    status_code = 200

    for i, (_, watchdog) in enumerate(pipelines):
        running, fps = watchdog.check()
        pipeline_states.append(
            {
                "id": i,
                "running": running,
                "fps": round(fps, 1),
            }
        )

        if not running:
            status_code = 500
            status = f"Pipeline {i} is not running"

    return JSONResponse(
        status_code=status_code,
        content={"status": status, "pipelines": pipeline_states},
    )


@app.post("/notify")
async def notify(request: Request):
    """Webhook endpoint to receive notifications from face recognition pipeline.

    Broadcasts the notification to all connected main page clients.
    """

    body = (await request.body()).decode("utf-8")

    # Broadcast notification to all connected clients on the main page
    for client in app.clients("/"):
        with client:
            ui.notify(body, type="info", position="top")

    return JSONResponse({"status": "notification sent", "message": body})


@ui.page("/")
def main_page():

    # View names
    VIEW_CONFIGURATION = "Configuration"
    VIEW_LIVE_STREAM = "Live Stream"

    face_map = degirum_face.ObjectMap()
    clips = clip_manager.list_clips()
    known_objects = clip_manager.db.list_objects()

    # Track current view selection
    current_view = {"selection": VIEW_CONFIGURATION}

    def sorted_known_objects():
        """Return known objects sorted by their attributes."""
        return sorted([str(a) for a in known_objects.values() if a])

    #
    # UI callbacks
    #

    def switch_view(view_name: str):
        """Switch between different views in the main area."""
        current_view["selection"] = view_name

        # Update button styling
        for name, btn in nav_buttons.items():
            if name == view_name:
                btn.classes(remove="text-blue-400", add="bg-blue-100 text-blue-800")
            else:
                btn.classes(remove="bg-blue-100 text-blue-800", add="text-blue-400")

        # Update content visibility
        if view_name == VIEW_CONFIGURATION:
            config_container.visible = True
            stream_container.visible = False
        elif view_name == VIEW_LIVE_STREAM:
            config_container.visible = False
            stream_container.visible = True

    async def delete_selected():
        """Delete the selected video clips."""
        selected = await clip_grid.get_selected_rows()
        if not selected:
            ui.notify("No rows selected")
            return

        selected_filenames = {r["file_name"] for r in selected}
        for f in selected_filenames:
            clip = clips.get(f.replace(".mp4", ""), {})
            for v in clip.values():
                clip_manager.remove_clip(v.object_name)

        refresh_clips()

    def show_hide_ann_controls(mode: str):
        """Show or hide annotation controls according to the mode."""

        if mode == "initial":
            ann_spinner.visible = False
            ann_grid.visible = False
            update_db_button.visible = False
            add_attr_button.visible = False
            ann_button.visible = False
        if mode == "original-clip":
            ann_spinner.visible = False
            ann_grid.visible = False
            update_db_button.visible = False
            add_attr_button.visible = False
            ann_button.visible = True
        elif mode == "annotation-in-progress":
            ann_spinner.visible = True
            ann_grid.visible = False
            update_db_button.visible = False
            add_attr_button.visible = False
            ann_button.visible = False
        elif mode == "annotated-clip":
            ann_spinner.visible = False
            ann_grid.visible = True
            update_db_button.visible = True
            add_attr_button.visible = True
            ann_button.visible = False

    async def on_clip_selected():
        """Handle the selection of a video clip."""
        selected = await clip_grid.get_selected_rows()
        if not selected:
            return

        filename = selected[0]["file_name"]
        file_stem, file_ext = os.path.splitext(filename)

        clip_collection = clips.get(file_stem)
        if not clip_collection:
            return

        clip = clip_collection.get("original")
        if not clip:
            return

        video_player.source = f"/video/{clip.object_name}"
        video_player.update()
        show_hide_ann_controls("original-clip")
        ann_button.visible = True
        annotation_label.text = (
            f"Selected: {filename}.\nClick `Annotate` to start annotation."
        )

    async def annotate_clip():
        """Annotate the selected video clip."""
        selected = await clip_grid.get_selected_rows()
        if not selected:
            ui.notify("No rows selected")
            return

        try:
            filename = selected[0]["file_name"]
            file_stem, file_ext = os.path.splitext(filename)

            show_hide_ann_controls("annotation-in-progress")
            annotation_label.text = f"Annotating {filename}..."

            nonlocal face_map
            face_map = await asyncio.to_thread(
                clip_manager.find_faces_in_clip, filename
            )

            annotation_label.text = f"{filename}: {len(face_map.map)} face(s) detected"

            annotated_filename = (
                file_stem
                + degirum_face.FaceClipManager.annotated_video_suffix
                + file_ext
            )
            clip_url = f"/video/{annotated_filename}"
            video_player.source = clip_url

            ann_rows = [
                {"id": face.track_id, "attributes": face.attributes or ""}
                for face in face_map.map.values()
            ]

            ann_grid.options["rowData"] = ann_rows
            ann_grid.update()
            refresh_clips()

        finally:
            show_hide_ann_controls("annotated-clip")

    async def update_embeddings_in_db():
        """Update the attributes from the annotation table to the database."""

        await ann_grid.load_client_data()  # updates grid.options["rowData"]
        updated = ann_grid.options["rowData"]  # now contains the latest data
        msg = ""
        for row in updated:
            track_id = row["id"]
            attr = row["attributes"]
            if not attr:
                continue  # Skip empty attributes

            face = face_map.get(track_id)
            if face is None:
                continue

            # find the object ID in the known objects list
            obj_id = next(
                (id for id, a in known_objects.items() if str(a) == str(attr)), None
            )
            if obj_id is None:
                continue

            # add embeddings
            clip_manager.db.add_embeddings(obj_id, face.embeddings, dedup=True)
            msg += f"{attr}: {len(face.embeddings)} embeddings\n"

        ui.notify("Database updated:\n" + msg, multi_line=True)

    async def on_confirm_new_attribute():
        """Handle the Add Attribute dialog"""
        attr = new_attr_input.value.strip()
        if attr:
            if any(attr == str(a) for a in known_objects.values()):
                ui.notify("Attribute already exists")
            else:
                obj_id = str(uuid.uuid4())
                known_objects[obj_id] = attr
                clip_manager.db.add_object(obj_id, attr)
                ann_grid.options["columnDefs"][1]["cellEditorParams"] = {
                    "values": sorted_known_objects()
                }
                ann_grid.update()
                ui.notify(f"Added attribute: {attr}")
        add_attr_dialog.close()

    async def db_info_dialog_open():
        """Open the dialog showing the embeddings DB info."""

        counts = sorted(
            clip_manager.db.count_embeddings().values(), key=lambda x: str(x[1])
        )
        rows = [
            {
                "attributes": str(c[1]),
                "counts": c[0],
            }
            for c in counts
        ]

        db_info_grid.options["rowData"] = rows
        db_info_grid.update()
        db_info_dialog.open()

    def refresh_clips():
        """Refresh the main page."""

        nonlocal clips
        clips = clip_manager.list_clips()
        clip_rows = [
            {
                "created": clip["original"]
                .last_modified.astimezone()
                .strftime("%Y-%m-%d %H:%M:%S"),
                "file_name": clip["original"].object_name,
                "annotated": "✅ viewed" if "annotated" in clip else "",
            }
            for clip in clips.values()
        ]
        clip_grid.options["rowData"] = clip_rows
        clip_grid.update()

    async def refresh_clips_async():
        refresh_clips()

    #
    # dialog for adding new attributes
    #
    add_attr_dialog = ui.dialog()
    with add_attr_dialog, ui.card():
        ui.label("Enter new attribute:")
        new_attr_input = ui.input(placeholder="new person name").classes("w-64")

        with ui.row():
            ui.button("✔ Confirm", on_click=on_confirm_new_attribute)
            ui.button("✖ Cancel", on_click=add_attr_dialog.close).props(
                "color=negative"
            )

    #
    # dialog for showing embeddings DB info
    #
    db_info_dialog = ui.dialog()
    with db_info_dialog, ui.card().classes("w-full max-w-lg"):

        db_info_grid = (
            ui.aggrid(
                {
                    "columnDefs": [
                        {
                            "headerName": "Person",
                            "field": "attributes",
                            "sortable": True,
                        },
                        {
                            "headerName": "Embedding Counts",
                            "field": "counts",
                            "sortable": True,
                            "maxWidth": 150,
                            "resizable": False,
                        },
                    ],
                    "defaultColDef": {
                        "resizable": True,
                        "sortable": True,
                        "filter": True,
                    },
                },
            )
            .classes("w-full")
            .style("flex-grow: 1")
        )

        ui.button("✔ OK", on_click=db_info_dialog.close)

    #
    # Main page layout with left navigation panel
    #
    with ui.row().classes("h-screen w-screen"):

        # Left navigation panel
        with ui.column().classes("w-48 h-full bg-white p-4 border-r border-gray-300"):
            ui.label("Navigation").classes("text-xl font-bold mb-6 text-gray-800")

            config_btn = (
                ui.button(
                    VIEW_CONFIGURATION, on_click=lambda: switch_view(VIEW_CONFIGURATION)
                )
                .classes("w-full mb-2 justify-start")
                .props("flat color=blue")
            )

            stream_btn = (
                ui.button(
                    VIEW_LIVE_STREAM, on_click=lambda: switch_view(VIEW_LIVE_STREAM)
                )
                .classes("w-full mb-2 justify-start")
                .props("flat color=blue")
            )

            # Store button references for styling updates
            nav_buttons = {VIEW_CONFIGURATION: config_btn, VIEW_LIVE_STREAM: stream_btn}

        # Main content area on the right
        with ui.column().classes("flex-1 h-full overflow-auto"):

            # Configuration view container
            config_container = ui.column().classes("w-full h-full")
            with config_container:
                with ui.row().classes("w-full h-[calc(100vh-2rem)] p-4"):

                    # Left side: video clips list card
                    with ui.card().classes(
                        "w-full h-full max-w-lg border border-gray-300 p-4 flex flex-col"
                    ):
                        ui.label("Video Clips of Captured Events").classes(
                            "text-xl font-bold mb-4"
                        )

                        clip_grid = (
                            ui.aggrid(
                                {
                                    "columnDefs": [
                                        {
                                            "headerName": "Created",
                                            "field": "created",
                                            "checkboxSelection": True,
                                            "sort": "desc",
                                        },
                                        {
                                            "headerName": "File Name",
                                            "field": "file_name",
                                        },
                                        {
                                            "headerName": "Viewed",
                                            "field": "annotated",
                                            "maxWidth": 150,
                                            "resizable": False,
                                        },
                                    ],
                                    "defaultColDef": {
                                        "resizable": True,
                                        "sortable": True,
                                        "filter": True,
                                    },
                                    "rowSelection": "multiple",
                                },
                            ).classes("w-full h-[calc(100vh-16rem)]")
                        ).on("selectionChanged", on_clip_selected)

                        with ui.row():
                            ui.button("ℹ DB Info", on_click=db_info_dialog_open)
                            ui.button(
                                "✖ Delete Selected", on_click=delete_selected
                            ).props("color=negative")
                            ui.button("⟳ Refresh", on_click=refresh_clips_async)

                    # Middle: Annotation card and video player
                    with ui.card().classes(
                        "w-full h-full max-w-lg border border-gray-300 p-4 flex flex-col"
                    ):
                        annotation_label = (
                            ui.label("Select a clip to view/annotate")
                            .classes("text-xl font-bold mb-4")
                            .style("white-space: pre-wrap")
                        )

                        # Annotation spinner
                        ann_spinner = (
                            ui.spinner(size="lg")
                            .props("color=primary")
                            .classes("absolute top-1/2 left-1/2")
                        )

                        # Video player
                        video_player = (
                            ui.video(src="")
                            .classes("w-full mb-4")
                            .style("max-height: 300px")
                        )

                        # Annotation button
                        ann_button = ui.button(
                            "🖉 Annotate", on_click=annotate_clip
                        ).classes("mb-4")

                        # Annotation grid
                        ann_grid = ui.aggrid(
                            {
                                "rowData": [],
                                "columnDefs": [
                                    {
                                        "headerName": "Track ID",
                                        "field": "id",
                                        "sortable": True,
                                        "filter": True,
                                    },
                                    {
                                        "headerName": "Person",
                                        "field": "attributes",
                                        "editable": True,
                                        "cellEditor": "agSelectCellEditor",
                                        "cellEditorParams": {
                                            "values": sorted_known_objects(),
                                        },
                                        "sortable": True,
                                        "filter": True,
                                    },
                                ],
                                "defaultColDef": {
                                    "resizable": True,
                                    "sortable": True,
                                    "filter": True,
                                },
                                "stopEditingWhenCellsLoseFocus": True,
                                "singleClickEdit": True,
                            }
                        ).classes("w-full h-64 mb-4")

                        with ui.row():
                            # Add attribute dialog button
                            add_attr_button = ui.button(
                                "✛ New Person", on_click=add_attr_dialog.open
                            )

                            # Update database button
                            update_db_button = ui.button(
                                "✔ Add Embeddings to DB",
                                on_click=update_embeddings_in_db,
                            ).props("color=negative")

            # Live Stream view container
            stream_container = ui.column().classes("w-full h-full")
            with stream_container:
                with ui.row().classes("w-full h-[calc(100vh-2rem)] p-4"):
                    with ui.card().classes(
                        "w-full h-full max-w-7xl border border-gray-300 p-4 flex flex-col"
                    ):
                        with ui.row().classes(
                            "w-full items-center justify-between mb-4"
                        ):
                            ui.label("Live Stream").classes("text-xl font-bold")
                            ui.button(
                                icon="open_in_new",
                                on_click=lambda: ui.navigate.to(
                                    "/stream", new_tab=True
                                ),
                            ).props("flat color=blue").tooltip("Open in New Tab")

                        assert context.client.request
                        host = context.client.request.headers.get("host", "localhost")
                        stream_url = f"http://{host.split(':')[0]}:8888/{config.live_stream_rtsp_url}"
                        ui.element("iframe").props(f'src="{stream_url}"').classes(
                            "w-full h-[calc(100vh-12rem)]"
                        )

    # Initialize view
    show_hide_ann_controls("initial")
    refresh_clips()
    switch_view(VIEW_CONFIGURATION)


@ui.page("/stream")
def stream_page():
    """Page to display the live stream of the face tracking application."""

    assert context.client.request
    host = context.client.request.headers.get("host", "localhost")
    stream_url = f"http://{host.split(':')[0]}:8888/{config.live_stream_rtsp_url}"
    ui.label("Live Stream").classes("text-xl font-bold mb-4")
    ui.element("iframe").props(f'src="{stream_url}"').classes(
        "w-[90%] mx-auto h-[calc(90vh)]"
    )


@ui.page("/video/{filename}")
async def serve_video(request: Request, filename: str):
    """Serve video with support for HTTP Range requests."""

    # Unquote filename (in case it has URL-encoded characters)
    filename = urllib.parse.unquote(filename)

    # Download full video into memory (later we can optimize this)
    video_bytes = clip_manager.download_clip(filename)
    file_size = len(video_bytes)

    # Extract Range header (e.g. 'bytes=0-')
    range_header = request.headers.get("range")
    content_type = "video/mp4"

    if range_header:
        # Parse start and end values
        range_value = range_header.strip().lower().replace("bytes=", "")
        start_str, end_str = range_value.split("-")
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
        end = min(end, file_size - 1)  # Don't exceed file size

        # Slice the requested byte range
        chunk = video_bytes[start : end + 1]
        content_length = len(chunk)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": content_type,
        }

        return Response(content=chunk, status_code=206, headers=headers)

    # No Range header — send full content
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": content_type,
    }

    return StreamingResponse(
        io.BytesIO(video_bytes), headers=headers, media_type=content_type
    )


# Run the NiceGUI application
# Note: `workers=1` because lancedb is not multi-process-safe
try:
    ui.run(title="Face Tracking", workers=1, reload=False, show=False)
except KeyboardInterrupt:
    print("Shutting down the application...")
