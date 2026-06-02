#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-marketcopilot}"
APP_ROOT="${APP_ROOT:-/srv/market-copilot}"
APP_BACKEND_ROOT="${APP_BACKEND_ROOT:-${APP_ROOT}/backend}"
ENV_DIR="${ENV_DIR:-/etc/market-copilot}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run this script as root or with sudo."
  exit 1
fi

install_packages() {
  if command -v dnf >/dev/null 2>&1; then
    dnf install -y \
      python3 \
      python3-pip \
      nginx \
      postgresql15 \
      postgresql15-server \
      git \
      gcc \
      gcc-c++ \
      make
    return
  fi

  if command -v yum >/dev/null 2>&1; then
    yum install -y \
      python3 \
      python3-pip \
      nginx \
      postgresql15 \
      postgresql15-server \
      git \
      gcc \
      gcc-c++ \
      make
    return
  fi

  if command -v apt-get >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y \
      python3 \
      python3-venv \
      nginx \
      postgresql \
      postgresql-contrib \
      git \
      build-essential
    return
  fi

  echo "Unsupported package manager. Expected dnf, yum, or apt-get."
  exit 1
}

install_packages

if ! id -u "${APP_USER}" >/dev/null 2>&1; then
  useradd --system --create-home --shell /bin/bash "${APP_USER}"
fi

mkdir -p "${APP_ROOT}" "${ENV_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${APP_ROOT}"

echo "Bootstrap complete."
echo "Next:"
echo "1. Copy backend code into ${APP_BACKEND_ROOT}"
echo "2. Create ${ENV_DIR}/backend.env from the template"
echo "3. Initialize and start PostgreSQL if needed"
echo "4. Set up PostgreSQL database/user"
echo "5. Install Python dependencies and run migrations"
