#!/usr/bin/env bash
set -euo pipefail

: "${AWS_REGION:?AWS_REGION is required}"
: "${IAM_ROLE_NAME:?IAM_ROLE_NAME is required}"
: "${INSTANCE_PROFILE_NAME:?INSTANCE_PROFILE_NAME is required}"
: "${ARTIFACT_BUCKET:?ARTIFACT_BUCKET is required}"

TRUST_DOC="$(mktemp)"
POLICY_DOC="$(mktemp)"
trap 'rm -f "${TRUST_DOC}" "${POLICY_DOC}"' EXIT

cat > "${TRUST_DOC}" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

cat > "${POLICY_DOC}" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::${ARTIFACT_BUCKET}",
        "arn:aws:s3:::${ARTIFACT_BUCKET}/*"
      ]
    }
  ]
}
EOF

aws iam create-role \
  --role-name "${IAM_ROLE_NAME}" \
  --assume-role-policy-document "file://${TRUST_DOC}"

aws iam put-role-policy \
  --role-name "${IAM_ROLE_NAME}" \
  --policy-name "${IAM_ROLE_NAME}-s3-artifacts-access" \
  --policy-document "file://${POLICY_DOC}"

#aws iam create-instance-profile \
#  --instance-profile-name "${INSTANCE_PROFILE_NAME}"

#aws iam add-role-to-instance-profile \
#  --instance-profile-name "${INSTANCE_PROFILE_NAME}" \
#  --role-name "${IAM_ROLE_NAME}"

echo "Created IAM role and use instance profile: ${IAM_ROLE_NAME} "
