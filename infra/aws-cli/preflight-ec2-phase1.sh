#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-marketcopilot}"
APP_BACKEND_ROOT="${APP_BACKEND_ROOT:-/srv/market-copilot/backend}"
APP_FRONTEND_ROOT="${APP_FRONTEND_ROOT:-/srv/market-copilot/frontend}"
ENV_FILE="${ENV_FILE:-/etc/market-copilot/backend.env}"
FRONTEND_ENV_FILE="${FRONTEND_ENV_FILE:-/etc/market-copilot/frontend.env}"
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
if [[ -d "${APP_FRONTEND_ROOT}" ]]; then
  echo "Frontend directory found: ${APP_FRONTEND_ROOT}"
fi
if [[ -f "${FRONTEND_ENV_FILE}" ]]; then
  echo "Frontend env file found: ${FRONTEND_ENV_FILE}"
fi

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

if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  echo
  echo "== Node runtime =="
  node --version
  npm --version
fi

if [[ -f "${FRONTEND_ENV_FILE}" ]]; then
  echo
  echo "== Frontend environment =="
  set -a
  source "${FRONTEND_ENV_FILE}"
  set +a

  frontend_required_vars=(
    MARKET_COPILOT_GRAPHQL_ENDPOINT
    MARKET_COPILOT_API_BASE_URL
    MARKET_COPILOT_SESSION_SECRET
  )

  for var_name in "${frontend_required_vars[@]}"; do
    if [[ -z "${!var_name:-}" ]]; then
      echo "Missing required frontend env var: ${var_name}"
      exit 1
    fi
  done

  if [[ "${MARKET_COPILOT_SESSION_SECRET}" == "REPLACE_ME_WITH_A_LONG_RANDOM_SECRET" ]]; then
    echo "Frontend session secret still contains placeholder value."
    exit 1
  fi

  echo "Frontend env vars are present."
fi

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
