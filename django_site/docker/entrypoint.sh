#!/bin/sh
set -e

cd /app

# Volume mounts may be root-owned on first run
mkdir -p /app/data /app/media /app/staticfiles
if [ "$(id -u)" = "0" ]; then
  chown -R app:app /app/data /app/media /app/staticfiles
fi

run_app() {
  if [ "$(id -u)" = "0" ]; then
    runuser -u app -- "$@"
  else
    "$@"
  fi
}

if [ "${DB_ENGINE:-sqlite}" = "postgresql" ]; then
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST:-db}..."
  until run_app python - <<'PY'
import os, sys
import psycopg

try:
    psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "db"),
        dbname=os.environ.get("POSTGRES_DB", "blog"),
        user=os.environ.get("POSTGRES_USER", "blog"),
        password=os.environ.get("POSTGRES_PASSWORD", "blog"),
        connect_timeout=3,
    ).close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  do
    sleep 1
  done
  echo "PostgreSQL is ready."
fi

run_app python manage.py migrate --noinput
run_app python manage.py collectstatic --noinput

echo "Starting: $*"
if [ "$(id -u)" = "0" ]; then
  exec runuser -u app -- "$@"
else
  exec "$@"
fi
