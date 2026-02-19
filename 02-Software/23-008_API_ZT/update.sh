#!/usr/bin/env bash
set -euo pipefail

SERVICE_USER="ztapi"

# Dossier où se trouve ce script => même niveau que main.py
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# Comme APP_DIR = <ROOT>/02-Software/23-008_API_ZT, ROOT = remonter de 2 niveaux
ROOT_DIR="$(realpath "${APP_DIR}/../..")"
VENV="${ROOT_DIR}/venv"

# Détection prod/dev selon le chemin
case "${ROOT_DIR}" in
  /opt/zt_api_prod)
    BRANCH="main"
    SERVICE="zt-api-prod"
    ;;
  /opt/zt_api_dev)
    BRANCH="develop"
    SERVICE="zt-api-dev"
    ;;
  *)
    echo "Erreur: ROOT_DIR inattendu: ${ROOT_DIR}"
    echo "Ce script doit être dans /opt/zt_api_prod/${APP_DIR##*/} (ou /opt/zt_api_dev/...)"
    exit 1
    ;;
esac

# Exiger root (pour systemctl). Git/pip seront faits en ztapi.
if [[ "${EUID}" -ne 0 ]]; then
  echo "Lance en root: sudo $0"
  exit 1
fi

echo "== Update: ROOT_DIR=${ROOT_DIR} | branch=${BRANCH} | service=${SERVICE} =="

# 1) Git update (en ztapi)
sudo -u "${SERVICE_USER}" -H bash -c "
  set -e
  git -C '${ROOT_DIR}' fetch --all --prune
  git -C '${ROOT_DIR}' checkout -f '${BRANCH}' || git -C '${ROOT_DIR}' checkout -f -b '${BRANCH}' 'origin/${BRANCH}'
  git -C '${ROOT_DIR}' reset --hard 'origin/${BRANCH}'
"

# 2) Deps (en ztapi)
sudo -u "${SERVICE_USER}" -H "${VENV}/bin/python" -m pip install -U pip setuptools wheel

if [[ -f "${APP_DIR}/requirements.txt" ]]; then
  sudo -u "${SERVICE_USER}" -H "${VENV}/bin/pip" install -r "${APP_DIR}/requirements.txt"
elif [[ -f "${ROOT_DIR}/requirements.txt" ]]; then
  sudo -u "${SERVICE_USER}" -H "${VENV}/bin/pip" install -r "${ROOT_DIR}/requirements.txt"
else
  echo "WARN: requirements.txt introuvable (skip deps)"
fi

# 3) Restart service
systemctl restart "${SERVICE}"
systemctl --no-pager -l status "${SERVICE}"
