# EC2 Setup Checklist: Phase 1 Congressional Source

## Purpose

This checklist turns the EC2 deployment design into an execution-ready setup path for the first congressional Phase 1 deployment.

It assumes:

- one EC2 instance
- Amazon Linux host
- one backend checkout at `/srv/market-copilot`
- one backend app root at `/srv/market-copilot/backend`
- one application user, for example `marketcopilot`

## 1. Host Preparation

- provision EC2 instance
- restrict SSH access to known operators
- open only `22`, `80`, and `443`
- install system packages:
  - `python3`
  - `python3-pip`
  - `nginx`
  - `postgresql15`
  - `postgresql15-server`
  - `git`
  - `gcc`
  - `gcc-c++`
  - `make`

## 2. Application Directories

- create `/srv/market-copilot`
- place backend code under `/srv/market-copilot/backend`
- create application-owned directories if local artifact mode is ever used

## 3. Python Environment

From `/srv/market-copilot/backend`:

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
```

## 4. PostgreSQL Setup

- initialize the database cluster if this is a fresh host
- enable and start PostgreSQL
- create database user
- create `market_copilot` database
- grant application user access

Typical Amazon Linux flow:

```bash
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

Then run migrations:

```bash
cd /srv/market-copilot/backend
.venv/bin/alembic upgrade head
```

## 5. Production Environment File

Create:

- `/etc/market-copilot/backend.env`

Minimum contents:

```bash
MARKET_COPILOT_ENVIRONMENT=production
MARKET_COPILOT_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/market_copilot
MARKET_COPILOT_API_HOST=127.0.0.1
MARKET_COPILOT_API_PORT=8000
MARKET_COPILOT_LOG_LEVEL=INFO
MARKET_COPILOT_NORMALIZATION_PROVIDER=openai
MARKET_COPILOT_OPENAI_API_KEY=REPLACE_ME
MARKET_COPILOT_OPENAI_MODEL=gpt-4.1-mini
MARKET_COPILOT_ARTIFACT_STORAGE_MODE=s3
MARKET_COPILOT_S3_BUCKET=REPLACE_ME
MARKET_COPILOT_S3_REGION=REPLACE_ME
MARKET_COPILOT_HOUSE_XML_SOURCE_URL=https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2026FD.xml
```

## 6. API Service

Create:

- `/etc/systemd/system/market-copilot-api.service`

Suggested unit:

```ini
[Unit]
Description=Market Copilot API
After=network.target postgresql.service

[Service]
User=marketcopilot
WorkingDirectory=/srv/market-copilot/backend
EnvironmentFile=/etc/market-copilot/backend.env
ExecStart=/srv/market-copilot/backend/.venv/bin/uvicorn market_copilot.api.app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable market-copilot-api
sudo systemctl start market-copilot-api
```

## 7. Nginx

Create an `Nginx` site that proxies:

- public `443` to `127.0.0.1:8000`

Minimum upstream block:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Also configure:

- TLS
- HTTP to HTTPS redirect

## 8. Cron Command

Create a cron entry for the application user:

```cron
15 6 * * * cd /srv/market-copilot/backend && . /etc/market-copilot/backend.env && .venv/bin/python -m market_copilot.ingestion.main >> /var/log/market-copilot-ingestion.log 2>&1
```

Adjust schedule based on the preferred daily ingestion window.

## 9. First Verification

After setup:

1. verify API service status
2. verify `curl http://127.0.0.1:8000/health`
3. run one manual scheduled-style ingestion command
4. inspect logs
5. inspect ingestion run and normalization job rows

Manual command:

```bash
cd /srv/market-copilot/backend
set -a && source /etc/market-copilot/backend.env && set +a
.venv/bin/python -m market_copilot.ingestion.main
```

## 10. Update Path

For the first release cycle:

1. update code on host
2. install dependency changes if needed
3. run migrations
4. restart API service
5. run one manual ingestion smoke test

## 11. Scope Guardrail

This setup is for the `2026+` congressional source only.

Do not expand the EC2 setup to pre-2026 historical ingestion or unrelated data domains during the Phase 1 deployment pass.
