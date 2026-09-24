"""Small dependency-free structured logging helper for this service."""
from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "service": getattr(record, "service", "unknown"),
            "event": getattr(record, "event", record.getMessage()),
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        for key in ("method", "path", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str, service: str) -> logging.Logger:
    logger = logging.getLogger(service)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def new_request_id(incoming: str | None = None) -> str:
    return incoming.strip()[:128] if incoming and incoming.strip() else str(uuid.uuid4())


def monotonic_ms() -> float:
    return time.perf_counter() * 1000
