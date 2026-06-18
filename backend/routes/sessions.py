"""Session history and report endpoints."""

from flask import Blueprint, jsonify, request

from backend.services.session_service import SessionService
from backend.utils.errors import NotFoundError

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/session/<int:session_id>", methods=["GET"])
def get_session(session_id: int):
    """GET /session/{id} — retrieve session details."""
    session = SessionService().get_by_id(session_id)
    if not session:
        raise NotFoundError(f"Session {session_id} not found")
    return jsonify({"success": True, "data": session.to_dict(include_frames=True)})


@sessions_bp.route("/history", methods=["GET"])
def get_history():
    """GET /history — paginated session list."""
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = int(request.args.get("offset", 0))
    service = SessionService()
    sessions = service.get_history(limit=limit, offset=offset)
    return jsonify({
        "success": True,
        "total": service.count_sessions(),
        "limit": limit,
        "offset": offset,
        "data": [s.to_dict() for s in sessions],
    })


@sessions_bp.route("/report/<int:session_id>", methods=["GET"])
def get_report(session_id: int):
    """GET /report/{id} — detailed report with recommendations."""
    session = SessionService().get_by_id(session_id)
    if not session:
        raise NotFoundError(f"Session {session_id} not found")
    return jsonify({"success": True, "data": session.to_report_dict()})


@sessions_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"success": True, "status": "healthy", "service": "motor-function-tracker"})
