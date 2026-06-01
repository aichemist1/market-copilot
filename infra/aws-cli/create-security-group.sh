#!/usr/bin/env bash
set -euo pipefail

: "${VPC_ID:?VPC_ID is required}"
: "${SECURITY_GROUP_NAME:?SECURITY_GROUP_NAME is required}"
: "${SSH_CIDR:?SSH_CIDR is required}"

#SG_ID="$(aws ec2 create-security-group \
#  --group-name "${SECURITY_GROUP_NAME}" \
#  --description "Security group for Market Copilot Phase 1 congressional backend" \
#  --vpc-id "${VPC_ID}" \
#  --query 'GroupId' \
#  --output text)"

#aws ec2 authorize-security-group-ingress \
#  --group-id "${SG_ID}" \
#  --ip-permissions \
#  "[{\"IpProtocol\":\"tcp\",\"FromPort\":22,\"ToPort\":22,\"IpRanges\":[{\"CidrIp\":\"${SSH_CIDR}\",\"Description\":\"Operator SSH\"}]},{\"IpProtocol\":\"tcp\",\"FromPort\":80,\"ToPort\":80,\"IpRanges\":[{\"CidrIp\":\"0.0.0.0/0\",\"Description\":\"HTTP\"}]},{\"IpProtocol\":\"tcp\",\"FromPort\":443,\"ToPort\":443,\"IpRanges\":[{\"CidrIp\":\"0.0.0.0/0\",\"Description\":\"HTTPS\"}]}]"

SG_ID="sg-02647b80a727ee37f"
#echo "Created security group: ${SG_ID}"
#echo "Export this for the next step:"
echo "export SECURITY_GROUP_ID=${SG_ID}"
echo "SECURITY_GROUP_ID=${SECURITY_GROUP_NAME}"
