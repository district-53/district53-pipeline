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

if ! id -u "$APP_USER" >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER"
fi


install -d -m 750 -o root -g "$APP_USER" "$ENV_DIR"

TMP=$(mktemp "${ENV_FILE}.XXXXXX")
trap 'rm -f "$TMP"' EXIT
cat > "$TMP" <<EOF
# Managed by infra/provision/app_set_up.sh. Manual changes will be overwritten.
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}
SECRET_KEY=${SECRET_KEY}
FLASK_DEBUG=0
EOF
chown root:"$APP_USER" "$TMP"
chmod 640 "$TMP"
mv "$TMP" "$ENV_FILE"
trap - EXIT


cat > "${APP_DIR}/.env" <<EOF
DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}
SECRET_KEY=${SECRET_KEY}
EOF
chmod 600 "${APP_DIR}/.env"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv python3-pip

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  python3 -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/pip" install -q -r "${APP_DIR}/requirements.txt"

echo "App node ready: ${ENV_FILE} -> ${DB_USER}@${DB_HOST}/${DB_NAME}, venv ${VENV_DIR}"
echo "Run the app as '${APP_USER}': sudo -u ${APP_USER} ${VENV_DIR}/bin/gunicorn --chdir ${APP_DIR} -b 0.0.0.0:8000 app:app"