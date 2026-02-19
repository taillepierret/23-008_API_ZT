#!/usr/bin/env bash
set -euo pipefail

### ===== CONFIG =====
REPO_URL="https://github.com/taillepierret/23-008_API_ZT.git"

# Dossiers séparés (Option A)
PROD_DIR="/opt/zt_api_prod"
DEV_DIR="/opt/zt_api_dev"

# Chemin du code (tel qu'il est dans ton repo)
APP_SUBDIR="02-Software/23-008_API_ZT"

# User systemd
SERVICE_USER="ztapi"
SERVICE_GROUP="ztapi"

# Ports
PROD_PORT="5000"
DEV_PORT="5001"

### ===== HELPERS =====
log(){ echo "[init] $*"; }

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    echo "Lance en root : sudo ./init.sh"
    exit 1
  fi
}

ensure_user() {
  if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
    log "Création de l'utilisateur système ${SERVICE_USER}..."
    useradd --system --create-home --home-dir "/home/${SERVICE_USER}" --shell /usr/sbin/nologin "${SERVICE_USER}"
  fi
}

apt_update_upgrade() {
  log "Mise à jour Raspberry Pi OS (apt update + full-upgrade)..."
  apt update -y
  DEBIAN_FRONTEND=noninteractive apt full-upgrade -y
  apt autoremove -y
}

install_deps() {
  log "Installation des dépendances..."
  apt install -y git ca-certificates python3 python3-venv python3-pip
}

clone_or_update() {
  local target_dir="$1"
  local branch="$2"

  mkdir -p "${target_dir}"
  chown -R "${SERVICE_USER}:${SERVICE_GROUP}" "${target_dir}"

  if [[ -d "${target_dir}/.git" ]]; then
    log "Repo déjà présent (${target_dir}), reset vers origin/${branch}..."
    sudo -u "${SERVICE_USER}" -H bash -c "
      cd '${target_dir}' &&
      git fetch origin '${branch}' &&
      git checkout -f '${branch}' || git checkout -f -b '${branch}' 'origin/${branch}' &&
      git reset --hard 'origin/${branch}'
    "
  else
    log "Clonage (${branch}) dans ${target_dir}..."
    sudo -u "${SERVICE_USER}" -H git clone --branch "${branch}" --single-branch "${REPO_URL}" "${target_dir}"
  fi
}

setup_venv_and_deps() {
  local base_dir="$1"
  local app_dir="${base_dir}/${APP_SUBDIR}"
  local venv_dir="${base_dir}/venv"

  if [[ ! -d "${app_dir}" ]]; then
    echo "ERREUR: Dossier app introuvable: ${app_dir}"
    exit 1
  fi

  log "Création venv: ${venv_dir}"
  if [[ ! -d "${venv_dir}" ]]; then
    sudo -u "${SERVICE_USER}" -H python3 -m venv "${venv_dir}"
  fi

  log "Installation requirements: ${app_dir}/requirements.txt"
  if [[ -f "${app_dir}/requirements.txt" ]]; then
    sudo -u "${SERVICE_USER}" -H bash -c "
      '${venv_dir}/bin/pip' install --upgrade pip wheel setuptools &&
      '${venv_dir}/bin/pip' install -r '${app_dir}/requirements.txt'
    "
  else
    log "ATTENTION: requirements.txt introuvable dans ${app_dir} (skip)."
  fi
}

write_service() {
  local service_name="$1"
  local base_dir="$2"
  local port="$3"
  local env_mode="$4"   # production / development

  local app_dir="${base_dir}/${APP_SUBDIR}"
  local venv_dir="${base_dir}/venv"
  local service_file="/etc/systemd/system/${service_name}.service"

  log "Écriture service systemd: ${service_file}"

  cat > "${service_file}" <<EOF
[Unit]
Description=${service_name}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
WorkingDirectory=${app_dir}
Environment=FLASK_APP=main.py
Environment=FLASK_ENV=${env_mode}
# Pour éviter le reloader multiple en systemd
Environment=WERKZEUG_RUN_MAIN=true
ExecStart=${venv_dir}/bin/python -m flask run --host 0.0.0.0 --port ${port}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
}

enable_services() {
  log "Activation des services..."
  systemctl daemon-reload
  systemctl enable --now zt-api-prod.service
  systemctl enable --now zt-api-dev.service
}

status_hint() {
  echo
  echo "=== DONE ==="
  echo "PROD: http://<IP_DU_PI>:${PROD_PORT}"
  echo "DEV : http://<IP_DU_PI>:${DEV_PORT}"
  echo
  echo "Logs:"
  echo "  journalctl -u zt-api-prod -f"
  echo "  journalctl -u zt-api-dev  -f"
  echo
}

### ===== MAIN =====
require_root
apt_update_upgrade
install_deps
ensure_user

clone_or_update "${PROD_DIR}" "main"
setup_venv_and_deps "${PROD_DIR}"

clone_or_update "${DEV_DIR}" "develop"
setup_venv_and_deps "${DEV_DIR}"

write_service "zt-api-prod" "${PROD_DIR}" "${PROD_PORT}" "production"
write_service "zt-api-dev"  "${DEV_DIR}"  "${DEV_PORT}"  "development"

enable_services
status_hint
