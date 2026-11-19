#!/bin/bash
set -euo pipefail

APP_DIR="/opt/hall"
VENV_DIR="/opt/venv"
ENV_DIR="/etc/hall"
ENV_FILE="${ENV_DIR}/app.env"
APP_USER="hall"

if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "ERROR: DB_PASSWORD is empty (check infra/secrets/db_password)" >&2
  exit 1
fi
if [[ -z "${SECRET_KEY:-}" ]]; then
  echo "ERROR: SECRET_KEY is empty (check infra/secrets/secret_key)" >&2
  exit 1
fi
if (( ${#SECRET_KEY} < 32 )); then
  echo "ERROR: SECRET_KEY must be at least 32 characters" >&2
  exit 1
fi
if [[ ! -f "${APP_DIR}/requirements.txt" ]]; then
  echo "ERROR: ${APP_DIR}/requirements.txt not found. Is the app folder synced?" >&2
  exit 1
fi

APP_HOME="/var/lib/${APP_USER}"
if ! id -u "$APP_USER" >/dev/null 2>&1; then
  useradd --system --home-dir "$APP_HOME" --shell /usr/sbin/nologin "$APP_USER"
fi
usermod -d "$APP_HOME" "$APP_USER"
install -d -m 750 -o "$APP_USER" -g "$APP_USER" "$APP_HOME"


install -d -m 750 -o root -g "$APP_USER" "$ENV_DIR"

cat > "$ENV_FILE" <<EOF
DATABASE_URL=postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}
SECRET_KEY=${SECRET_KEY}
FLASK_DEBUG=0
EOF
chown root:"$APP_USER" "$ENV_FILE"
chmod 640 "$ENV_FILE"


export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  python3 -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/pip" install -q -r "${APP_DIR}/requirements.txt"

echo "App node ready: env ${ENV_FILE}, venv ${VENV_DIR}"
echo "Start the app: sudo -u ${APP_USER} ${VENV_DIR}/bin/gunicorn --chdir ${APP_DIR} -b 0.0.0.0:8000 --workers 2 --access-logfile - app:app"