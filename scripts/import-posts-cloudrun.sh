#!/usr/bin/env bash
# Import Hugo markdown posts into Cloud SQL (prod).
set -euo pipefail

PROJECT="${GCP_PROJECT:-matheus-cloud-pessoal}"
REGION="${GCP_REGION:-southamerica-east1}"
INSTANCE="${CLOUD_SQL_INSTANCE:-blog-postgres}"
PORT="${CLOUD_SQL_PROXY_PORT:-9470}"
CONN="${PROJECT}:${REGION}:${INSTANCE}"

command -v cloud-sql-proxy >/dev/null || {
  echo "Install: gcloud components install cloud-sql-proxy" >&2
  exit 1
}

PG_PASS="$(gcloud secrets versions access latest --secret=matheus-blog-postgres-password --project="$PROJECT")"
DJANGO_KEY="$(gcloud secrets versions access latest --secret=matheus-blog-django-secret-key --project="$PROJECT")"

cloud-sql-proxy "$CONN" --port "$PORT" &
PROXY_PID=$!
trap 'kill $PROXY_PID 2>/dev/null || true' EXIT
sleep 2

cd "$(dirname "$0")/../django_site"

export DB_ENGINE=postgresql
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT="$PORT"
export POSTGRES_DB=blog
export POSTGRES_USER=blog
export POSTGRES_PASSWORD="$PG_PASS"
export DJANGO_SECRET_KEY="$DJANGO_KEY"
export DEBUG=False
export GCP_LOAD_SECRETS=False

echo "Importing posts..."
uv run python manage.py import_hugo
uv run python manage.py update_hugo_posts

echo "Done. Posts in prod DB."
