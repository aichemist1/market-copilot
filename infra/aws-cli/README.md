# AWS CLI Provisioning: Phase 1 Congressional Source

This directory contains the active infrastructure provisioning path for the Phase 1 congressional backend.

Approach:

- AWS CLI first
- small shell scripts
- one EC2 host
- one S3 bucket
- one IAM role and instance profile
- one security group

This path is intentionally lightweight for the current project stage.

## Layout

- `env.example`
- `create-s3-bucket.sh`
- `create-iam-role.sh`
- `create-security-group.sh`
- `launch-ec2.sh`
- `bootstrap-ec2-phase1.sh`
- `preflight-ec2-phase1.sh`
- `backend.env.production.example`
- `frontend.env.production.example`
- `market-copilot-api.service`
- `market-copilot-frontend.service`
- `nginx-market-copilot.conf`
- `install-app-on-ec2.sh`
- `install-frontend-on-ec2.sh`
- `create-cron-entry.sh`

## Usage Order

1. copy `env.example` to `.env`
2. fill in real AWS values
3. source the env file
4. run the scripts in order

Example:

```bash
cd /Users/dev/Documents/market-copilot/infra/aws-cli
cp env.example .env
set -a && source .env && set +a
./create-s3-bucket.sh
./create-iam-role.sh
./create-security-group.sh
./launch-ec2.sh
```

## Post-Launch Host Setup

After the EC2 instance is running:

1. SSH to the host
2. run `bootstrap-ec2-phase1.sh` as root
3. copy backend code to `/srv/market-copilot`
4. create `/etc/market-copilot/backend.env` from `backend.env.production.example`
5. create `/etc/market-copilot/frontend.env` from `frontend.env.production.example`
6. create the PostgreSQL database and user
7. run `install-app-on-ec2.sh` as root
8. run `install-frontend-on-ec2.sh` as root
9. run `create-cron-entry.sh` as root

Recommended before install:

```bash
sudo bash preflight-ec2-phase1.sh
```

## Frontend Deployment Shape

The first production-shaped frontend deployment is:

- Next.js app running on `127.0.0.1:3000`
- backend API running on `127.0.0.1:8000`
- `Nginx` routing:
  - `/` to frontend
  - `/graphql` to backend
  - `/health` to backend

This allows public routes such as:

- `/login`
- `/register`
- `/signals`
- `/trade-explorer`

## Scope Guardrail

These scripts are for the `2026+` congressional Phase 1 deployment only.

Do not expand them into a broader platform layer until the current source phase proves it is necessary.
