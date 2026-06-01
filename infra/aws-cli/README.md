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

## Scope Guardrail

These scripts are for the `2026+` congressional Phase 1 deployment only.

Do not expand them into a broader platform layer until the current source phase proves it is necessary.
