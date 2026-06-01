#!/usr/bin/env bash
set -euo pipefail

: "${AWS_REGION:?AWS_REGION is required}"
: "${ARTIFACT_BUCKET:?ARTIFACT_BUCKET is required}"

if [[ "${AWS_REGION}" == "us-east-1" ]]; then
  aws s3api create-bucket \
    --bucket "${ARTIFACT_BUCKET}"
else
  aws s3api create-bucket \
    --bucket "${ARTIFACT_BUCKET}" \
    --create-bucket-configuration "LocationConstraint=${AWS_REGION}"
fi

aws s3api put-public-access-block \
  --bucket "${ARTIFACT_BUCKET}" \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws s3api put-bucket-versioning \
  --bucket "${ARTIFACT_BUCKET}" \
  --versioning-configuration Status=Enabled

echo "Created and configured bucket: ${ARTIFACT_BUCKET}"
