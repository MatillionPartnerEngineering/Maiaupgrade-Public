---
name: migration-sns-authentication
description: Detect and guide remediation of SNS Message components migrated from Matillion ETL that require AWS authentication configuration in DPC. Covers IAM role setup, topic ARN validation, and common failure patterns.
---

# SNS Message AWS Authentication Setup

## When to Use
- When migrated pipelines contain `sns-message` components
- When SNS notifications fail with authorization or credential errors after migration
- When triaging pipeline failures where SNS is on the failure transition path

## Why This Matters
Migrated `sns-message` components retain their Topic ARN and message configuration but may fail in DPC due to **AWS authentication differences**. In METL, SNS components inherited the EC2 instance's IAM role automatically. In DPC, authentication depends on the deployment model (Full SaaS vs Hybrid SaaS) and requires explicit cloud credential configuration.

SNS components are typically used for error notification, audit logging, and job status alerts — placed on `failure` transitions as alerting mechanisms.

---

## Detection

### Find All SNS Components

```
Pattern: type: "sns-message"
Glob: **/*.orch.yaml
```

### Common Error Messages

| Error Message | Root Cause | Fix |
|--------------|-----------|-----|
| `AuthorizationError` | IAM role lacks `sns:Publish` permission | Add SNS publish policy to execution role |
| `InvalidClientTokenId` | AWS credentials not configured or expired | Configure cloud credentials in DPC environment |
| `Not authorized to perform: SNS:Publish` | Missing IAM policy | Add `sns:Publish` to IAM role |
| Connection timeout | Network/VPC configuration issue | Check agent network access to SNS endpoint |

---

## SNS Component Structure

```yaml
    SNS Notification:
      type: "sns-message"
      parameters:
        componentName: "SNS Notification"
        snsTopicArn: "arn:aws:sns:us-west-2:123456789012:My-Notification-Topic"
        subject: "Pipeline Failure Alert"
        message: "Component ${audit_component} failed: ${audit_message}"
```

**Key parameters:**
- `snsTopicArn` — The ARN of the SNS topic to publish to
- `subject` — Email subject line
- `message` — Notification body (supports variable interpolation)

---

## Authentication in DPC

### Hybrid SaaS (Agent-based)

The agent's execution role (IAM role attached to the EC2 instance or ECS task) must include:

```json
{
  "Effect": "Allow",
  "Action": "sns:Publish",
  "Resource": "arn:aws:sns:*:123456789012:*"
}
```

If **cloud credentials** are configured on the DPC environment, they override the agent's role.

### Full SaaS (Matillion-hosted)

Cloud credentials **must** be configured on the DPC environment. The credential's IAM role needs `sns:Publish` permission on the target topic ARNs.

---

## Remediation Steps

### Step 1: Inventory All SNS Topics

Search for unique Topic ARNs across all pipelines and document each unique ARN with its AWS account/region.

### Step 2: Verify IAM Permissions

For each SNS topic ARN, confirm the DPC execution role has `sns:Publish` permission. This is a **customer/infrastructure task**.

### Step 3: Verify Cloud Credentials in DPC

1. Navigate to **Environment Settings → Cloud Credentials** in DPC
2. Confirm credentials are configured for the correct AWS account
3. Verify the credential's IAM role has SNS publish permissions

### Step 4: Test a Single SNS Component

Run a pipeline containing one SNS component to verify delivery.

---

## Triage Priority

SNS components are typically **non-blocking** for data pipeline functionality:

| Priority | Scenario | Action |
|----------|----------|--------|
| LOW | SNS on failure transitions only | Pipeline data flow works; fix SNS after core validation |
| MEDIUM | SNS in audit/logging chains | Pipeline completes but audit trail incomplete |
| HIGH | SNS in conditional logic | Pipeline behavior depends on SNS success/failure |

**Recommendation:** Treat SNS authentication as a Phase 4 (post-validation) task. Focus on data pipeline functionality first, then enable notifications.

---

## Common Patterns in Migrated Pipelines

### Error Notification Pattern
```yaml
    Data Load:
      type: "database-query"
      transitions:
        success:
        - "Next Step"
        failure:
        - "SNS Error Alert"
    SNS Error Alert:
      type: "sns-message"
      parameters:
        snsTopicArn: "arn:aws:sns:us-west-2:123456789012:ETL-Notifications"
        subject: "ETL Failure: ${audit_component}"
        message: "Error: ${audit_message}"
```

### Audit Chain Pattern
```yaml
      postProcessing:
        updateScalarVariables:
        - - "audit_component"
          - "${sysvar.thisComponent.name}"
        - - "audit_status"
          - "${sysvar.thisComponent.status}"
        - - "audit_message"
          - "${sysvar.thisComponent.message}"
```

The `postProcessing` block captures component status into variables, which are then referenced in SNS `message` parameters.

---

## Key Considerations

- **SNS failures should not block migration validation** — they are secondary to data pipeline correctness
- **Topic ARNs are environment-specific** — verify the ARN matches the target AWS account; consider parameterizing with variables
- **Cross-account SNS** requires additional IAM trust policies
- **Variable interpolation** in SNS messages works the same in DPC as METL
- **Skipped SNS components** are common in migrated pipelines — verify `skipped` state before troubleshooting