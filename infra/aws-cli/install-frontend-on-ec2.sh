#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/srv/market-copilot}"
APP_FRONTEND_ROOT="${APP_FRONTEND_ROOT:-${APP_ROOT}/frontend}"
FRONTEND_ENV_FILE="${FRONTEND_ENV_FILE:-/etc/market-copilot/frontend.env}"
FRONTEND_SERVICE_TEMPLATE="${FRONTEND_SERVICE_TEMPLATE:-/srv/market-copilot/infra/aws-cli/market-copilot-frontend.service}"
NGINX_TEMPLATE="${NGINX_TEMPLATE:-/srv/market-copilot/infra/aws-cli/nginx-market-copilot.conf}"
NPM_BIN="${NPM_BIN:-npm}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run this script as root or with sudo."
  exit 1
fi

if [[ ! -d "${APP_FRONTEND_ROOT}" ]]; then
  echo "Frontend directory not found: ${APP_FRONTEND_ROOT}"
  exit 1
fi

if [[ ! -f "${FRONTEND_ENV_FILE}" ]]; then
  echo "Frontend environment file not found: ${FRONTEND_ENV_FILE}"
  exit 1
fi

if ! command -v "${NPM_BIN}" >/dev/null 2>&1; then
  echo "npm not found: ${NPM_BIN}"
  exit 1
fi

cd "${APP_FRONTEND_ROOT}"

set -a
source "${FRONTEND_ENV_FILE}"
set +a

if [[ -f package-lock.json ]]; then
  "${NPM_BIN}" ci
else
  "${NPM_BIN}" install
fi
"${NPM_BIN}" run build

cp "${FRONTEND_SERVICE_TEMPLATE}" /etc/systemd/system/market-copilot-frontend.service
systemctl daemon-reload
systemctl enable market-copilot-frontend
systemctl restart market-copilot-frontend

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

echo "Frontend install complete."
echo "Verify:"
echo "curl -I http://127.0.0.1:3000/login"
