#!/usr/bin/env bash
# One-off: create/update Django superuser against Cloud SQL (prod).
#   DJANGO_SUPERUSER_PASSWORD='...' ./scripts/bootstrap-cloudrun-admin.sh
set -euo pipefail

PROJECT="${GCP_PROJECT:-matheus-cloud-pessoal}"
REGION="${GCP_REGION:-southamerica-east1}"
INSTANCE="${CLOUD_SQL_INSTANCE:-blog-postgres}"
EMAIL="${DJANGO_SUPERUSER_EMAIL:-matheusthurlernf@gmail.com}"
USERNAME="${DJANGO_SUPERUSER_USERNAME:-matheus}"

if [[ -z "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  echo "Set DJANGO_SUPERUSER_PASSWORD (not stored in repo)." >&2
  exit 1
fi

CONN="${PROJECT}:${REGION}:${INSTANCE}"
PORT="${CLOUD_SQL_PROXY_PORT:-9470}"

command -v cloud-sql-proxy >/dev/null || {
  echo "Install: gcloud components install cloud-sql-proxy" >&2
  exit 1
}

PG_PASS="$(gcloud secrets versions access latest \
  --secret=matheus-blog-postgres-password --project="$PROJECT")"
DJANGO_KEY="$(gcloud secrets versions access latest \
  --secret=matheus-blog-django-secret-key --project="$PROJECT")"

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
export DJANGO_SUPERUSER_EMAIL="$EMAIL"
export DJANGO_SUPERUSER_USERNAME="$USERNAME"

uv run python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]

user, _ = User.objects.get_or_create(
    username=username,
    defaults={"email": email, "is_staff": True, "is_superuser": True},
)
user.email = email
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()
print(f"Admin ready: {user.email} (username={user.username})")
PY

uv run python manage.py axes_reset_username "$USERNAME" 2>/dev/null || true
uv run python manage.py axes_reset 2>/dev/null || true

echo "Login: https://matheusthurler.com.br/admin/ (username=$USERNAME, not email)"
