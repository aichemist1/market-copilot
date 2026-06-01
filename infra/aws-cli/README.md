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
- `backend.env.production.example`
- `market-copilot-api.service`
- `nginx-market-copilot.conf`
- `install-app-on-ec2.sh`
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
5. create the PostgreSQL database and user
6. run `install-app-on-ec2.sh` as root
7. run `create-cron-entry.sh` as root

## Scope Guardrail

These scripts are for the `2026+` congressional Phase 1 deployment only.

Do not expand them into a broader platform layer until the current source phase proves it is necessary.
