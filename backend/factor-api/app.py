from __future__ import annotations

from flask import Flask, g, jsonify, request

from config import settings
from factor_lookup import load_registry, lookup_factor
from observability import configure_logging, monotonic_ms, new_request_id

SERVICE = "carbonguard-factor-api"
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
    return jsonify({"status": "ok", "service": SERVICE, "year": settings.year, "request_id": g.request_id})


@app.get("/ready")
def ready():
    try:
        registry = load_registry()
        if not registry:
            raise RuntimeError("Factor registry is empty")
        return jsonify({"status": "ready", "service": SERVICE, "year": settings.year, "request_id": g.request_id})
    except Exception:
        logger.exception(
            "factor registry readiness failed",
            extra={"service": SERVICE, "event": "readiness_failed", "request_id": g.request_id},
        )
        return _error(503, "NOT_READY", "Factor registry is unavailable.")


@app.post("/lookup-factor")
def lookup():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error(400, "INVALID_JSON", "Request body must be a JSON object.")

    required = ["scope", "activity", "unit", "year"]
    missing = [key for key in required if data.get(key) in (None, "")]
    if missing:
        return _error(400, "MISSING_FIELDS", "Required factor lookup fields are missing.", missing_fields=missing)

    try:
        result = lookup_factor(
            scope=str(data["scope"]),
            activity=str(data["activity"]),
            unit=str(data["unit"]),
            year=int(data["year"]),
            category=data.get("category"),
            fuel_subtype=data.get("fuel_subtype") or data.get("subtype"),
        )
    except (TypeError, ValueError) as exc:
        logger.warning(
            "invalid factor lookup request",
            extra={"service": SERVICE, "event": "invalid_lookup", "request_id": g.request_id},
        )
        return _error(400, "INVALID_REQUEST", "Invalid factor lookup request.", detail=str(exc))

    logger.info(
        "factor lookup completed",
        extra={
            "service": SERVICE,
            "event": "factor_lookup",
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
