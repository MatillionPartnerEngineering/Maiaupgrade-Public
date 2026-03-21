---
name: migration-s3-iam-credential-setup
description: Detect and guide remediation of S3-dependent components (S3 Load, Excel Query, SFTP) migrated from Matillion ETL that require AWS IAM credential configuration in DPC. Covers cloud credential setup, IAM role validation, and common access errors.
---

# S3 and IAM Credential Setup for Migrated Pipelines

## When to Use
- When migrated pipelines that interact with AWS S3 fail with access/credential errors
- When Excel Query, database-query (S3 staging), or SFTP components fail after migration
- When auditing AWS credential configuration for DPC environments

## Why This Matters
Migrated pipelines that interact with AWS services (S3, SNS, SES, etc.) may fail due to **AWS credential configuration differences** between METL and DPC. In METL, components inherited the EC2 instance's IAM role automatically. In DPC, credential resolution depends on the deployment model and explicit cloud credential configuration.

---

## Detection

### Find S3-Dependent Components

```
# Excel Query components loading from S3
Pattern: storageType.*Amazon S3
Glob: **/*.orch.yaml

# S3 staging areas
Pattern: s3StagingArea
Glob: **/*.orch.yaml

# IAM Role ARN references
Pattern: iamRoleArn
Glob: **/*.orch.yaml

# S3 URLs
Pattern: s3://
Glob: **/*.orch.yaml
```

### Common Error Messages

| Error Message | Root Cause | Fix |
|--------------|-----------|-----|
| `InvalidAccessKeyId` | AWS credentials not configured or expired | Configure cloud credentials in DPC environment |
| `AccessDenied` / `403 Forbidden` | IAM role lacks S3 permissions | Add S3 read/write policy to execution role |
| `NoSuchBucket` | S3 bucket doesn't exist or wrong region | Verify bucket name and region |
| `SignatureDoesNotMatch` | Credential mismatch or clock skew | Regenerate credentials |
| `The specified bucket does not exist` | Bucket name typo or deleted | Verify S3 bucket exists |

---

## Authentication Models in DPC

### Hybrid SaaS (Agent-based)

```
Component → Agent execution role → AWS services
         ↓ (overridden by)
         Environment cloud credentials → AWS services
```

1. **Default:** Components use the agent's IAM execution role (attached to EC2/ECS)
2. **Override:** If cloud credentials are configured on the DPC environment, they take precedence

### Full SaaS (Matillion-hosted)

```
Component → Environment cloud credentials → AWS services
```

Cloud credentials **must** be configured. No default execution role exists.

---

## Required IAM Permissions

### For S3 Staging (COPY/UNLOAD Operations)

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject",
    "s3:ListBucket",
    "s3:GetBucketLocation"
  ],
  "Resource": [
    "arn:aws:s3:::my-staging-bucket",
    "arn:aws:s3:::my-staging-bucket/*"
  ]
}
```

### For Excel Query (S3 Source Files)

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::my-data-bucket",
    "arn:aws:s3:::my-data-bucket/*"
  ]
}
```

### For Redshift COPY via IAM Role

Redshift needs to assume an IAM role to execute COPY/UNLOAD commands:

```json
{
  "Effect": "Allow",
  "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::123456789012:role/my-redshift-role"
}
```

The `iamRoleArn` parameter in components specifies this Redshift execution role.

---

## Remediation

### Step 1: Verify Cloud Credentials in DPC

This is a **customer/admin task**:
1. Navigate to **DPC → Environments → [Environment] → Cloud Credentials**
2. Verify AWS credentials are configured
3. Confirm the IAM role/user has the required S3 permissions

### Step 2: Verify S3 Bucket Access

For each S3 bucket referenced in the project:
- Bucket exists in the correct AWS region
- IAM credentials have read/write access
- Bucket policy doesn't block the DPC execution role

### Step 3: Verify IAM Role ARN

For components using `iamRoleArn`:
- The role exists in the target AWS account
- The warehouse cluster is authorized to assume this role
- The role has S3 access for staging operations

### Step 4: Handle Placeholder/Invalid ARNs

```yaml
# ❌ Placeholder ARN
        iamRoleArn: "arn:aws:iam::000000000000:role/placeholder"

# ✅ Valid ARN
        iamRoleArn: "arn:aws:iam::123456789012:role/my-redshift-role"
```

Replace with the correct ARN from the customer's AWS account.

---

## SFTP Component Credentials

SFTP components use different credential parameters:

```yaml
    SFTP Put Object:
      type: "sftp-put-object"
      parameters:
        targetUrl3: "sftp://sftp-server.example.com/path/"
        targetUsername2: "sftp-user"
        targetPassword: "MY_SFTP_SECRET"  # TEXT_SECRET_REF
```

**Key parameters:**
- `targetPassword` — uses `TEXT_SECRET_REF` (same plain string format as `password`)
- `targetUsername2` — plaintext username
- `targetSftpKey` — optional SSH key reference

---

## Triage Priority

| Component Type | Impact | Priority |
|---------------|--------|----------|
| `database-query` / `rds-query` with S3 staging | Core data loading fails | 🔴 HIGH |
| `excel-query` loading from S3 | Specific data sources unavailable | 🟡 MEDIUM |
| SFTP components | File transfer fails | 🟡 MEDIUM |
| SNS components | Notifications fail (non-blocking) | 🟢 LOW |

---

## Verification

1. **Sample an excel-query component** that loads from S3 — confirms S3 read access
2. **Run a pipeline with database-query** using S3 staging — confirms COPY/UNLOAD access
3. **Check task history** for specific error messages if failures occur
4. **Verify all S3 URLs** point to existing buckets and paths

---

## Key Considerations

- **Cloud credentials are environment-level** — one configuration covers all components in the environment
- **IAM role ARN is component-level** — each component can specify its own execution role
- **S3 staging area `[Environment Default]`** uses the environment's configured S3 bucket — verify it exists
- **Cross-account S3 access** requires bucket policies in addition to IAM roles
- **S3 Transfer Acceleration** (`useAcceleratedEndpoint`) requires explicit bucket configuration
- **Maia cannot modify AWS IAM policies** — document requirements and hand off to the customer as action items