#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-marketcopilot}"
APP_ROOT="${APP_ROOT:-/srv/market-copilot}"
APP_BACKEND_ROOT="${APP_BACKEND_ROOT:-${APP_ROOT}/backend}"
ENV_FILE="${ENV_FILE:-/etc/market-copilot/backend.env}"
SERVICE_TEMPLATE="${SERVICE_TEMPLATE:-/srv/market-copilot/infra/aws-cli/market-copilot-api.service}"
NGINX_TEMPLATE="${NGINX_TEMPLATE:-/srv/market-copilot/infra/aws-cli/nginx-market-copilot.conf}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run this script as root or with sudo."
  exit 1
fi

if [[ ! -d "${APP_BACKEND_ROOT}" ]]; then
  echo "Backend directory not found: ${APP_BACKEND_ROOT}"
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Environment file not found: ${ENV_FILE}"
  exit 1
fi

cd "${APP_BACKEND_ROOT}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Required Python runtime not found: ${PYTHON_BIN}"
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

"${PYTHON_BIN}" -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
.venv/bin/alembic upgrade head

cp "${SERVICE_TEMPLATE}" /etc/systemd/system/market-copilot-api.service
systemctl daemon-reload
systemctl enable market-copilot-api
systemctl restart market-copilot-api

if [[ -d /etc/nginx/conf.d ]]; then
  cp "${NGINX_TEMPLATE}" /etc/nginx/conf.d/market-copilot.conf
elif [[ -d /etc/nginx/sites-available && -d /etc/nginx/sites-enabled ]]; then
  cp "${NGINX_TEMPLATE}" /etc/nginx/sites-available/market-copilot
  ln -sf /etc/nginx/sites-available/market-copilot /etc/nginx/sites-enabled/market-copilot
  rm -f /etc/nginx/sites-enabled/default
else
  echo "Unsupported nginx layout."
  exit 1
fi

nginx -t
systemctl restart nginx

echo "Application install complete."
echo "Health check:"
echo "curl -fsS http://127.0.0.1:8000/health"
