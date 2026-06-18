"""Analysis endpoints: video and frame processing."""

from flask import Blueprint, current_app, jsonify, request

from backend.services.session_service import SessionService
from backend.services.video_processor import VideoProcessor
from backend.utils.errors import ValidationError
from backend.utils.geometry import decode_base64_image, save_upload

analyze_bp = Blueprint("analyze", __name__)


def _get_processor() -> VideoProcessor:
    return VideoProcessor(current_app.config)


@analyze_bp.route("/analyze-video", methods=["POST"])
def analyze_video():
    """
    POST /analyze-video
    Accepts multipart video file upload.
    Returns session metrics and session ID.
    """
    if "video" not in request.files and "file" not in request.files:
        raise ValidationError("No video file provided. Use 'video' or 'file' field.")

    file = request.files.get("video") or request.files.get("file")
    if not file or file.filename == "":
        raise ValidationError("Empty file upload.")

    allowed = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        raise ValidationError(f"Unsupported format. Allowed: {', '.join(allowed)}")

    upload_path = save_upload(file, current_app.config["UPLOAD_DIR"])
    processor = _get_processor()

    try:
        result = processor.process_video(
            upload_path,
            save_overlay=True,
            upload_dir=current_app.config["UPLOAD_DIR"],
        )
        session = SessionService().create_from_analysis(
            result,
            source_type="video",
            source_filename=file.filename,
        )
        return jsonify({
            "success": True,
            "session_id": session.id,
            "data": session.to_dict(),
        }), 201
    finally:
        processor.close()


@analyze_bp.route("/analyze-frame", methods=["POST"])
def analyze_frame():
    """
    POST /analyze-frame
    Accepts either:
      - multipart image file (field: image or file)
      - JSON body with base64 image (field: image_base64)
    """
    processor = _get_processor()
    source_filename = None

    try:
        if request.content_type and "multipart" in request.content_type:
            file = request.files.get("image") or request.files.get("file")
            if not file or file.filename == "":
                raise ValidationError("No image file provided.")
            import cv2
            upload_path = save_upload(file, current_app.config["UPLOAD_DIR"])
            source_filename = file.filename
            image = cv2.imread(str(upload_path))
            if image is None:
                raise ValidationError("Could not decode image file.")
        else:
            data = request.get_json(silent=True) or {}
            b64 = data.get("image_base64") or data.get("image")
            if not b64:
                raise ValidationError("Provide 'image_base64' in JSON or upload an image file.")
            image = decode_base64_image(b64)

        result = processor.process_frame(
            image,
            frame_index=0,
            timestamp=0.0,
            include_overlay=True,
            include_landmarks=True,
        )

        session = SessionService().create_from_frame(result, source_filename)

        response_data = {
            "success": result.get("pose_detected", False),
            "session_id": session.id,
            "data": result if result.get("pose_detected") else {"error": result.get("error")},
        }
        if result.get("pose_detected"):
            response_data["data"]["session_summary"] = session.to_dict()

        status = 201 if result.get("pose_detected") else 422
        return jsonify(response_data), status
    finally:
        processor.close()
