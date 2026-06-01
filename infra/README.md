# Infrastructure

This directory contains infrastructure code and deployment support assets for Market Intelligence Copilot.

Current focus:

- Phase 1 congressional source
- `2026+` data only
- single-instance EC2 deployment shape

Recommended structure:

- `aws-cli/`
- `scripts/`
- `env/`

Current provisioning preference:

- AWS CLI first
- lightweight shell scripts
- minimal abstraction

Application code remains in [`backend/`](/Users/dev/Documents/market-copilot/backend). Infrastructure code stays separate from the application layer on purpose.

Active provisioning docs:

- [`aws-cli/README.md`](/Users/dev/Documents/market-copilot/infra/aws-cli/README.md)
