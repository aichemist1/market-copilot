#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-marketcopilot}"
APP_BACKEND_ROOT="${APP_BACKEND_ROOT:-/srv/market-copilot/backend}"
ENV_FILE="${ENV_FILE:-/etc/market-copilot/backend.env}"
CRON_SCHEDULE="${CRON_SCHEDULE:-15 6 * * *}"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

if ! id -u "${APP_USER}" >/dev/null 2>&1; then
  echo "Application user not found: ${APP_USER}"
  exit 1
fi

CRON_LINE="${CRON_SCHEDULE} cd ${APP_BACKEND_ROOT} && set -a && . ${ENV_FILE} && set +a && ${PYTHON_BIN} -m market_copilot.ingestion.main >> /var/log/market-copilot-ingestion.log 2>&1"

( crontab -u "${APP_USER}" -l 2>/dev/null | grep -v 'market_copilot.ingestion.main' ; echo "${CRON_LINE}" ) | crontab -u "${APP_USER}" -

echo "Installed cron entry for ${APP_USER}:"
echo "${CRON_LINE}"
