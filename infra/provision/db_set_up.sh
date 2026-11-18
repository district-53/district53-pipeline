#!/bin/bash
set -euo pipefail

PG_VERSION=16
PG_CONF_DIR="/etc/postgresql/${PG_VERSION}/main"

if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "ERROR: DB_PASSWORD is empty" >&2
  exit 1
fi
if (( ${#DB_PASSWORD} < 16 )); then
  echo "ERROR: DB_PASSWORD must be at least 16 characters." >&2
  exit 1
fi


if ! dpkg -s "postgresql-${PG_VERSION}" >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y "postgresql-${PG_VERSION}"
fi

cat > "${PG_CONF_DIR}/conf.d/hall.conf" <<EOF
listen_addresses = 'localhost,${DB_LISTEN}'
password_encryption = 'scram-sha-256'
EOF


HBA="${PG_CONF_DIR}/pg_hba.conf"

cat > "$HBA" <<'EOF'
# TYPE  DATABASE  USER      ADDRESS           METHOD

# Local admin access
local   all       postgres                    peer
local   all       all                         peer

# Password access from the db VM itself
host    all       all       127.0.0.1/32      scram-sha-256
host    all       all       ::1/128           scram-sha-256
EOF

for ip in $APP_IPS; do
  printf 'host    %s      %s  %s/32  scram-sha-256\n' "$DB_NAME" "$DB_USER" "$ip"
done >> "$HBA"


systemctl enable --now postgresql >/dev/null
systemctl restart postgresql

for _ in $(seq 1 30); do
  pg_isready -q -h localhost && break
  sleep 1
done
pg_isready -h localhost

export DB_NAME DB_USER DB_PASSWORD
cd /tmp
runuser -u postgres -- psql -v ON_ERROR_STOP=1 -q <<'SQL'
\getenv db_name DB_NAME
\getenv db_user DB_USER
\getenv db_password DB_PASSWORD

SELECT format('CREATE ROLE %I LOGIN', :'db_user')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'db_user') \gexec

SELECT format('ALTER ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD %L', :'db_user', :'db_password') \gexec

SELECT format('CREATE DATABASE %I OWNER %I', :'db_name', :'db_user')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'db_name') \gexec
SELECT format('ALTER DATABASE %I OWNER TO %I', :'db_name', :'db_user') \gexec

SELECT format('REVOKE ALL ON DATABASE %I FROM PUBLIC', :'db_name') \gexec
SQL

echo "PostgreSQL ${PG_VERSION} ready: database '${DB_NAME}', user '${DB_USER}', listening on localhost,${DB_LISTEN}"
echo "Allowed clients: ${APP_IPS}"
