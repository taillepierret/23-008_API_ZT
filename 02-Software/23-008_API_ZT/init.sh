#!/usr/bin/env bash
set -euo pipefail

# ====== A ADAPTER ======
REPO_URL="https://github.com/taillepierret/23-008_API_ZT.git"       # ex: git@github.com:toi/zt_api.git
PROD_DIR="/opt/zt_api_prod"
DEV_DIR="/opt/zt_api_dev"

PROD_BRANCH="main"
DEV_BRANCH="develop"

PROD_PORT="5000"
DEV_PORT="5001"

# Dossier où se trouve main.py (d'après ton WorkingDirectory actuel)
APP_SUBDIR="02-Software/23-008_API_ZT"

SERVICE_USER="ztapi"
SERVICE_GROUP="ztapi"

# (Optionnel) fichiers d'env séparés
PROD_ENV_FILE="/etc/zt-api/prod.env"
DEV_ENV_FILE="/etc/zt-api/dev.env"
# =======================

ensure_user() {
  if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
    useradd --system --create-home --shell /usr/sbin/nologin "${SERVICE_USER}"
  fi
}

clone_or_update() {
  local dir="$1"
  local branch="$2"

  if [[ ! -d "${dir}/.git" ]]; then
    git clone "${REPO_URL}" "${dir}"
  fi

  cd "${dir}"
  git fetch --all --prune
  git checkout "${branch}"
  git pull --ff-only origin "${branch}"
}

ensure_venv_and_deps() {
  local dir="$1"
  local app_dir="${dir}/${APP_SUBDIR}"
  local venv="${dir}/venv"

  if [[ ! -d "${venv}" ]]; then
    python3 -m venv "${venv}"
  fi

  "${venv}/bin/python" -m pip install -U pip setuptools wheel

  # requirements.txt : on essaie d'abord dans APP_DIR, sinon à la racine
  if [[ -f "${app_dir}/requirements.txt" ]]; then
    "${venv}/bin/pip" install -r "${app_dir}/requirements.txt"
  elif [[ -f "${dir}/requirements.txt" ]]; then
    "${venv}/bin/pip" install -r "${dir}/requirements.txt"
  else
    echo "WARN: requirements.txt introuvable dans ${app_dir} ni dans ${dir} (je skip l'install deps)"
  fi
}

write_service() {
  local service_name="$1"
  local dir="$2"
  local port="$3"
  local flask_env="$4"
  local env_file="$5"

  local app_dir="${dir}/${APP_SUBDIR}"
  local venv="${dir}/venv"
  local unit="/etc/systemd/system/${service_name}.service"

  mkdir -p /etc/zt-api

  cat > "${unit}" <<EOF
[Unit]
Description=${service_name}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
WorkingDirectory=${app_dir}

# Env "logique"
Environment=FLASK_ENV=${flask_env}

# Env fichier (optionnel)
EnvironmentFile=-${env_file}

# IMPORTANT: app explicite + pas de reloader/debugger sous systemd
ExecStart=${venv}/bin/python -m flask --app main:app run --host 0.0.0.0 --port ${port} --no-reload --no-debugger

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
}

main() {
  ensure_user

  # Permissions (optionnel mais propre)
  mkdir -p "${PROD_DIR}" "${DEV_DIR}"
  chown -R "${SERVICE_USER}:${SERVICE_GROUP}" "${PROD_DIR}" "${DEV_DIR}"

  # PROD
  clone_or_update "${PROD_DIR}" "${PROD_BRANCH}"
  ensure_venv_and_deps "${PROD_DIR}"
  write_service "zt-api-prod" "${PROD_DIR}" "${PROD_PORT}" "production" "${PROD_ENV_FILE}"

  # DEV
  clone_or_update "${DEV_DIR}" "${DEV_BRANCH}"
  ensure_venv_and_deps "${DEV_DIR}"
  write_service "zt-api-dev" "${DEV_DIR}" "${DEV_PORT}" "development" "${DEV_ENV_FILE}"

  systemctl daemon-reload
  systemctl enable --now zt-api-prod zt-api-dev

  echo
  echo "OK. Status:"
  systemctl --no-pager -l status zt-api-prod zt-api-dev
}

main "$@"
