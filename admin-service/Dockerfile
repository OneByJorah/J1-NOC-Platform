FROM python:3.11-slim

WORKDIR /app

COPY main.py .

RUN pip install --no-cache-dir fastapi uvicorn pydantic cryptography

# Healthcheck — use Python instead of curl
HEALTHCHECK --interval=10s --timeout=3s --retries=3 --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/api/health', timeout=3)" || exit 1

EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]