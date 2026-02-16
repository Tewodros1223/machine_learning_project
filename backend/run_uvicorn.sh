#!/usr/bin/env bash
set -euo pipefail

# Helper script to run uvicorn with optional TLS
CERT=${SSL_CERT_FILE:-}
KEY=${SSL_KEY_FILE:-}

if [[ -n "$CERT" && -n "$KEY" ]]; then
  echo "Starting uvicorn with TLS"
  exec uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-certfile "$CERT" --ssl-keyfile "$KEY"
else
  echo "Starting uvicorn without TLS"
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
