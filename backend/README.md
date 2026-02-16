# Backend (FastAPI)

Requirements: Python 3.10+ and optionally GPU for face model.

Install dependencies (prefer virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run locally (SQLite by default):

```bash
export DATABASE_URL="sqlite:///./dev.db"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If you want to use Postgres, set `DATABASE_URL` to your Postgres connection string.

Face model: If `facenet-pytorch` and `torch` are installed the service will use a pretrained InceptionResnetV1 model. Otherwise a deterministic fallback embedding is used (not secure).

Security and limits
- Rate limiting: a simple in-memory per-IP limiter is enabled by default. Configure with `RATE_LIMIT_MAX_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` environment variables.
- Max upload size: set `MAX_UPLOAD_SIZE` (bytes) to limit incoming payloads. Requests with a larger `Content-Length` are rejected with `413`.

HTTPS (TLS)
For local TLS testing you can run `uvicorn` with `--ssl-keyfile` and `--ssl-certfile` flags, or use the included helper script `run_uvicorn.sh` which reads `SSL_CERT_FILE` and `SSL_KEY_FILE` env vars.

Example (self-signed cert):

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
export SSL_CERT_FILE="$(pwd)/cert.pem"
export SSL_KEY_FILE="$(pwd)/key.pem"
# Prefer running via Makefile or with bash to avoid needing exec bits:
bash run_uvicorn.sh
# Or: make run
```

If you get "Permission denied" for `./run_uvicorn.sh`, either run it with `bash run_uvicorn.sh` or use `make run`. To make it executable locally run:

```bash
chmod +x run_uvicorn.sh
```

