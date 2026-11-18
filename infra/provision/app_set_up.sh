#!/bin/bash
set -euo pipefail

APP_DIR="/opt/hall"
VENV_DIR="/opt/venv"

if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "ERROR: DB_PASSWORD is empty (check infra/secrets/db_password)" >&2
  exit 1
fi

if [[ -z "${SECRET_KEY:-}" ]]; then
  echo "ERROR: SECRET_KEY is empty (check infra/secrets/secret_key)" >&2
  exit 1
fi

cat > "${APP_DIR}/.env" <<EOF
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}
SECRET_KEY=${SECRET_KEY}
EOF
chmod 600 "${APP_DIR}/.env"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv python3-pip

if [[ -f "${APP_DIR}/requirements.txt" ]]; then
  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/pip" install --upgrade pip
  "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"
fi

echo "App node ready: .env created at ${APP_DIR}/.env pointing to ${DB_HOST}"