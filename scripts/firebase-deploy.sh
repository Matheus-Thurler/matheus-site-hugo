#!/usr/bin/env bash
# Deploy Firebase Hosting (live channel). Used by Django CI after Cloud Run promote.
set -euo pipefail

PROJECT_ID="${FIREBASE_PROJECT_ID:-matheus-cloud-pessoal}"
CONFIG="${FIREBASE_CONFIG:-firebase.json}"

npm install -g firebase-tools

set +e
output=$(firebase deploy --only hosting --project "$PROJECT_ID" --config "$CONFIG" --non-interactive 2>&1)
code=$?
set -e

echo "$output"

if [[ $code -ne 0 ]] && echo "$output" | grep -qi "current active version"; then
  echo "Site already up to date on Firebase Hosting live channel."
  exit 0
fi

exit $code
