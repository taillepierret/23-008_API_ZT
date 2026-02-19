#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="zt-api-prod"
BASE_DIR="/opt/zt_api_prod"
APP_DIR="${BASE_DIR}/02-Software/23-008_API_ZT"
VENV_DIR="${BASE_DIR}/venv"
BRANCH="main"
SERVICE_USER="ztapi"

echo "[update-prod] Stop service..."
systemctl stop "${SERVICE_NAME}"

echo "[update-prod] Update repo (reset --hard origin/${BRANCH})..."
sudo -u "${SERVICE_USER}" -H bash -c "
  cd '${BASE_DIR}' &&
  git fetch origin '${BRANCH}' &&
  git checkout -f '${BRANCH}' || git checkout -f -b '${BRANCH}' 'origin/${BRANCH}' &&
  git reset --hard 'origin/${BRANCH}'
"

echo "[update-prod] Reinstall python deps..."
if [[ -f "${APP_DIR}/requirements.txt" ]]; then
  sudo -u "${SERVICE_USER}" -H bash -c "
    '${VENV_DIR}/bin/pip' install -r '${APP_DIR}/requirements.txt'
  "
fi

echo "[update-prod] Start service..."
systemctl start "${SERVICE_NAME}"

echo "[update-prod] Status:"
systemctl --no-pager --full status "${SERVICE_NAME}" || true
