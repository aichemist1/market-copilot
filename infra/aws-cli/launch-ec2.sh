#!/usr/bin/env bash
set -euo pipefail

: "${AMI_ID:?AMI_ID is required}"
: "${INSTANCE_TYPE:?INSTANCE_TYPE is required}"
: "${SUBNET_ID:?SUBNET_ID is required}"
: "${SECURITY_GROUP_ID:?SECURITY_GROUP_ID is required}"
: "${KEY_NAME:?KEY_NAME is required}"
: "${INSTANCE_PROFILE_NAME:?INSTANCE_PROFILE_NAME is required}"
: "${EC2_NAME:?EC2_NAME is required}"

INSTANCE_ID="$(aws ec2 run-instances \
  --image-id "${AMI_ID}" \
  --instance-type "${INSTANCE_TYPE}" \
  --subnet-id "${SUBNET_ID}" \
  --security-group-ids "${SECURITY_GROUP_ID}" \
  --iam-instance-profile "Name=${INSTANCE_PROFILE_NAME}" \
  --associate-public-ip-address \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":40,"VolumeType":"gp3"}}]' \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${EC2_NAME}},{Key=Project,Value=market-copilot},{Key=Environment,Value=${ENVIRONMENT}}]" \
  --query 'Instances[0].InstanceId' \
  --output text)"

echo "Launched EC2 instance: ${INSTANCE_ID}"
echo "Public IP:"
aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
