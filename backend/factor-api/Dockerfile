FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 appuser

COPY app.py config.py factor_lookup.py observability.py factors.json ./

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=2)"

CMD ["sh", "-c", "gunicorn --bind ${FACTOR_API_HOST:-0.0.0.0}:${PORT:-${FACTOR_API_PORT:-8000}} --access-logfile - --error-logfile - app:app"]
