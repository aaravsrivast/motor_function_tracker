"""Custom API exceptions and error handlers."""

from flask import jsonify


class APIError(Exception):
    """Base API error with HTTP status code."""

    status_code = 400

    def __init__(self, message: str, status_code: int = None, payload: dict = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload or {}


class NotFoundError(APIError):
    status_code = 404


class ValidationError(APIError):
    status_code = 400


def register_error_handlers(app):
    """Register global Flask error handlers."""

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        response = {"success": False, "error": error.message, **error.payload}
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(413)
    def handle_payload_too_large(error):
        return jsonify({"success": False, "error": "File too large. Max 100MB."}), 413

    @app.errorhandler(500)
    def handle_internal(error):
        return jsonify({"success": False, "error": "Internal server error"}), 500
