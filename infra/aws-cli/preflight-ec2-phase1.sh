#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-marketcopilot}"
APP_BACKEND_ROOT="${APP_BACKEND_ROOT:-/srv/market-copilot/backend}"
ENV_FILE="${ENV_FILE:-/etc/market-copilot/backend.env}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

echo "== OS =="
cat /etc/os-release

echo
echo "== Python =="
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Missing required Python binary: ${PYTHON_BIN}"
  exit 1
fi
"${PYTHON_BIN}" --version

echo
echo "== Application paths =="
test -d "${APP_BACKEND_ROOT}" || { echo "Missing backend directory: ${APP_BACKEND_ROOT}"; exit 1; }
test -f "${ENV_FILE}" || { echo "Missing env file: ${ENV_FILE}"; exit 1; }
echo "Backend directory found: ${APP_BACKEND_ROOT}"
echo "Env file found: ${ENV_FILE}"

echo
echo "== Environment =="
set -a
source "${ENV_FILE}"
set +a

required_vars=(
  MARKET_COPILOT_DATABASE_URL
  MARKET_COPILOT_NORMALIZATION_PROVIDER
  MARKET_COPILOT_OPENAI_API_KEY
  MARKET_COPILOT_ARTIFACT_STORAGE_MODE
  MARKET_COPILOT_S3_BUCKET
  MARKET_COPILOT_S3_REGION
  MARKET_COPILOT_HOUSE_XML_SOURCE_URL
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required env var: ${var_name}"
    exit 1
  fi
done

if [[ "${MARKET_COPILOT_S3_REGION}" == "REPLACE_ME" || "${MARKET_COPILOT_S3_BUCKET}" == "REPLACE_ME" ]]; then
  echo "S3 env vars still contain placeholder values."
  exit 1
fi

echo "Required env vars are present."

echo
echo "== Database client =="
if command -v psql >/dev/null 2>&1; then
  echo "psql is installed."
else
  echo "psql is not installed."
  exit 1
fi

if [[ -x "${APP_BACKEND_ROOT}/.venv/bin/python" ]]; then
  echo
  echo "== Database connectivity =="
  cd "${APP_BACKEND_ROOT}"
  .venv/bin/python - <<'PY'
from market_copilot.settings import get_settings
from sqlalchemy import create_engine, text

settings = get_settings()
engine = create_engine(settings.database_url, future=True)
with engine.connect() as conn:
    row = conn.execute(text("select current_database(), current_user")).one()
    print({"database": row[0], "user": row[1]})
PY
else
  echo
  echo "== Database connectivity =="
  echo "Skipping app-level DB connectivity check because .venv is not present yet."
fi

echo
echo "Preflight passed."
