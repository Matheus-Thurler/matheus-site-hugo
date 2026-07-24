#!/usr/bin/env bash
# Deploy Hugo static build to a preview channel (rollback). Does not touch live (Django).
set -euo pipefail

PROJECT_ID="${FIREBASE_PROJECT_ID:-matheus-cloud-pessoal}"
CHANNEL="${FIREBASE_HUGO_CHANNEL:-hugo-backup}"
CONFIG="${FIREBASE_CONFIG:-firebase.hugo.json}"
EXPIRES="${FIREBASE_CHANNEL_EXPIRES:-90d}"

if [[ ! -d public ]] || [[ -z "$(ls -A public 2>/dev/null || true)" ]]; then
  echo "Error: Hugo public/ is missing or empty. Run hugo --minify first."
  exit 1
fi

npm install -g firebase-tools

firebase hosting:channel:deploy "$CHANNEL" \
  --project "$PROJECT_ID" \
  --config "$CONFIG" \
  --expires "$EXPIRES" \
  --non-interactive

echo "Hugo backup channel: https://${CHANNEL}--${PROJECT_ID}.web.app"
