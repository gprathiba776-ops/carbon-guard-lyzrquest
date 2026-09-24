from __future__ import annotations

from flask import Flask, g, jsonify, request

from calculator import calculate_emissions
from config import settings
from observability import configure_logging, monotonic_ms, new_request_id

SERVICE = "carbonguard-calculator-api"
logger = configure_logging(settings.log_level, SERVICE)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024


def _error(status_code: int, error_code: str, message: str, **extra):
    payload = {
        "status": "ERROR",
        "error_code": error_code,
        "message": message,
        "request_id": getattr(g, "request_id", None),
    }
    payload.update(extra)
    return jsonify(payload), status_code


@app.before_request
def before_request():
    g.request_id = new_request_id(request.headers.get("X-Request-ID"))
    g.started_ms = monotonic_ms()


@app.after_request
def after_request(response):
    response.headers["X-Request-ID"] = g.request_id
    logger.info(
        "request completed",
        extra={
            "service": SERVICE,
            "event": "request_completed",
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": round(monotonic_ms() - g.started_ms, 2),
        },
    )
    return response


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": SERVICE, "request_id": g.request_id})


@app.get("/ready")
def ready():
    try:
        if not callable(calculate_emissions):
            raise RuntimeError("Calculator function unavailable")
        return jsonify({"status": "ready", "service": SERVICE, "request_id": g.request_id})
    except Exception:
        logger.exception(
            "calculator readiness failed",
            extra={"service": SERVICE, "event": "readiness_failed", "request_id": g.request_id},
        )
        return _error(503, "NOT_READY", "Calculator is unavailable.")


@app.post("/calculate")
def calculate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error(400, "INVALID_JSON", "Request body must be a JSON object.")

    required = ["quantity", "factor_value", "factor_unit", "factor_status"]
    missing = [key for key in required if key not in data]
    if missing:
        return _error(400, "MISSING_FIELDS", "Required calculation fields are missing.", missing_fields=missing)

    result = calculate_emissions(
        quantity=data.get("quantity"),
        factor_value=data.get("factor_value"),
        factor_unit=data.get("factor_unit"),
        factor_status=data.get("factor_status"),
    )
    logger.info(
        "calculation completed",
        extra={
            "service": SERVICE,
            "event": "calculation",
            "request_id": g.request_id,
        },
    )
    return jsonify(result), 200


@app.errorhandler(400)
def bad_request(error):
    return _error(400, "BAD_REQUEST", "Invalid request.")


@app.errorhandler(404)
def not_found(error):
    return _error(404, "NOT_FOUND", "Endpoint not found.")


@app.errorhandler(413)
def too_large(error):
    return _error(413, "PAYLOAD_TOO_LARGE", "Request body exceeds the service limit.")


@app.errorhandler(500)
def internal_error(error):
    logger.exception(
        "unhandled application error",
        extra={"service": SERVICE, "event": "internal_error", "request_id": getattr(g, "request_id", None)},
    )
    return _error(500, "INTERNAL_ERROR", "Internal server error.")
