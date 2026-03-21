---
name: migration-salesforce-query-load
description: Salesforce Query and Salesforce Load component gotchas, authentication patterns, API selection, and migration guidance for Matillion ETL to DPC migration.
---

# Migration Salesforce Query & Load

## When to Use
- When migrating pipelines that use Salesforce Query or Salesforce Load components
- When Salesforce authentication (OAuth, tokens) fails after migration
- When row counts are inconsistent between Salesforce extract runs
- When the Salesforce Load component is greyed out or not visible in DPC Designer
- When customers are unsure whether to use Salesforce Query or Salesforce Load

## Why This Matters
Salesforce components have undergone significant changes between METL and DPC, including a deprecation/un-deprecation cycle on the Query component that causes real customer confusion. OAuth authentication failures are the #1 technical failure mode, and silent data issues (row count variance, missing archived records, column casing changes) make Salesforce extracts high-risk during migration.

## Migration Behaviour

When migrating from METL, Salesforce components **automatically load as the Salesforce Query component**. Most customers choose to upgrade these to the **Salesforce Load** component, as it is the actively maintained component that receives future updates from Matillion.

## Strategic Context — Which Component to Use

The Salesforce Query component is **deprecated for Snowflake projects** and is superseded by the Salesforce Load component, which offers both full and incremental loading.

### Platform-Specific Guidance

| Platform | Component to Use | Notes |
|----------|-----------------|-------|
| **Snowflake** | **Salesforce Load** (Required for new pipelines) | Salesforce Query is deprecated; existing pipelines continue to work but may appear greyed out |
| **Databricks** | **Salesforce Query** | Continue using Salesforce Query |
| **Amazon Redshift** | **Salesforce Query** | Continue using Salesforce Query |

### Migration Guidance
- **METL → DPC (Snowflake):** Salesforce Query will import automatically, but should be replaced with Salesforce Load. The greyed-out appearance in Designer indicates replacement is needed.
- **METL → DPC (Databricks/Redshift):** Continue using Salesforce Query as-is.
- Salesforce Load adds **Incremental Load** capability (high-water mark based) not available in Salesforce Query — this is a significant upgrade for customers doing frequent syncs.

### Key Differences: Salesforce Query vs Salesforce Load

| Feature | Salesforce Query | Salesforce Load |
|---------|-----------------|----------------|
| Full load | ✅ | ✅ |
| Incremental load (high-water mark) | ❌ | ✅ |
| Auth methods | Username & Password, OAuth 2.0 Authorization Code, None | Username & Password, OAuth 2.0 Authorization Code, OAuth 2.0 Client Credentials, None |
| Load strategy options | Recreates/truncates target table each run | Replace, Truncate and Insert, Fail if Exists, Append |
| Cloud storage destination | ❌ | ✅ (direct to S3/Azure/GCS) |
| Snowflake projects | Deprecated | ✅ Active |
| Databricks / Redshift | ✅ Active | ❌ Not available |

> ⚠️ **Warning:** The Salesforce Query component is potentially destructive. If the target table undergoes a structure change, it will be recreated. Otherwise it is truncated. Setting `Recreate Target Table` to Off prevents both.

---

## Gotcha #1 — Salesforce Components Greyed Out in Designer

**Severity: 🔴 Critical**

### Symptom
Salesforce components appear greyed out in Designer with a message indicating a newer version is available.

### Two Distinct Scenarios

| Scenario | Cause | Action |
|----------|-------|--------|
| **Salesforce Query greyed out (Snowflake)** | Component is deprecated for Snowflake | Replace with Salesforce Load |
| **Salesforce Load greyed out** | A newer component version has been released | Update component to latest version |

### Impact
Customers who have just completed migration (updating all Salesforce Query → Salesforce Load) may find Load components greyed out later due to a new version release. This is normal DPC behaviour — component version updates occur periodically.

### Guidance
- Set expectations proactively that **component version updates will occur** in DPC
- Advise customers to build upgrade processes into their DPC governance model
- If the component is **not visible at all** (not greyed out, but missing), check:
  1. Agent version — ensure it includes the Salesforce Load component
  2. Agent manifest is correctly configured
  3. For Customer-Hosted Agent (CHA) customers, verify component availability by cloud/warehouse combination

---

## Gotcha #2 — OAuth / Token Authentication Failures

**Severity: 🔴 Critical**

The #1 technical failure mode for Salesforce components.

### Common Patterns

| Pattern | Root Cause | Fix |
|---------|-----------|-----|
| "Grant type not supported" | Salesforce Connected App doesn't have the correct OAuth flow enabled (e.g., Username-Password flow disabled in newer Salesforce orgs) | Use OAuth 2.0 JWT Bearer or Connected App with proper scopes |
| Token refresh failures mid-pipeline | OAuth tokens expiring during long-running jobs | Ensure "Refresh Token" scope is included in Connected App permissions |
| Unexpected Security Token prompt | Mismatch between auth method settings in the DPC connection profile | Verify connection profile auth method matches the Salesforce Connected App configuration |

### Remediation
- Verify the **Salesforce Connected App** has the correct grant types enabled (`client_credentials` or `authorization_code` depending on setup)
- For orgs that have **disabled the Username-Password OAuth flow**, use OAuth 2.0 JWT Bearer or Connected App with proper scopes
- Check if the **"Refresh Token" scope** is included in Connected App permissions for long-running jobs

---

## Gotcha #3 — Inconsistent Row Counts

**Severity: 🟠 High**

### Symptom
Row counts vary significantly between runs of the same Salesforce extract — particularly when running inside an iterator vs. independently.

Example pattern:
- Independent run: **175K rows** ✅
- Inside iterator: **132K rows** ❌
- Independent again: **175K rows** ✅

### Root Cause
When the Salesforce Query component runs **inside an iterator**, pagination behaviour can be affected — particularly if the iterator passes a variable that influences the SOQL query scope.

### Guidance
- **Never rely on row count alone** to validate Salesforce extracts — use key field checksum or record ID comparison
- When using Salesforce Query inside an **iterator**, test in isolation first to confirm row counts are stable
- Understand how **QueryAll vs Query** behaviour differs (see Gotcha #5)

---

## Gotcha #4 — API Type Selection: Bulk vs REST vs SOAP

**Severity: 🟠 High**

Three API modes are available in the Salesforce Query component:

| API Mode | Best For | Gotchas |
|----------|----------|--------|
| **REST API** | Small/medium datasets, real-time | Hits API governor limits on large orgs |
| **Bulk API 1.0** | Large datasets (async) | Can time out if Salesforce org is under load |
| **Bulk API 2.0** (Recommended for large) | Large datasets, simpler pagination | Doesn't support all SOQL operations (e.g., ORDER BY on non-indexed fields) |

### Guidance
- For **>50K records**, default to Bulk API 2.0
- Set appropriate **API call budgets** and monitor Salesforce org API usage
- Avoid complex ORDER BY clauses with Bulk API
- Customers defaulting to REST on large orgs will hit governor limits

---

## Gotcha #5 — QueryAll / Archived Records Not Returning

**Severity: 🟠 High — Silent Data Loss Risk**

The QueryAll operation (which includes soft-deleted and archived records) was the default in older versions — this changed. Customers relying on deleted/archived record retrieval may silently miss data after component updates.

### Guidance
- Explicitly confirm whether customers need **soft-deleted or archived records**
- If yes, verify that **QueryAll is explicitly selected** in the component configuration — don't assume it's the default
- This is a **silent data loss risk** — critical for compliance-sensitive customers (e.g., financial services)

---

## Gotcha #6 — Column Casing: PascalCase vs Lowercase

**Severity: 🟡 Medium**

Column name casing from the Salesforce Query component changed between versions — downstream transformations that referenced lowercase field names broke silently.

### Guidance
- After any component version upgrade, **validate column casing** in the output
- Use explicit column aliasing in downstream SQL where casing-sensitive targets are in use (e.g., Snowflake with `QUOTED_IDENTIFIERS_IGNORE_CASE = FALSE`)
- This is a **migration gotcha** — customers moving from METL to DPC or upgrading agent versions should explicitly test column name output

---

## Gotcha #7 — Salesforce Load "In" Comparator Bug

**Severity: 🟡 Medium**

The `IN` comparator in the Salesforce Load filter conditions has been confirmed as a bug in certain component versions.

### Guidance
- If customers need IN list filtering, advise using **SOQL directly** via a custom query rather than the visual filter builder
- Check whether a fix has been released in newer component versions before advising workarounds

---

## Gotcha #8 — AWS Access Error from Salesforce Query (CHA)

**Severity: 🟡 Medium**

Surfaces when the DPC agent doesn't have the correct IAM permissions for the S3 staging bucket used during Salesforce bulk extract. Relevant for **Customer-Hosted Agents** where IAM roles are customer-managed.

### Guidance
- For CHA customers using Salesforce Query with Bulk API, ensure the **agent's IAM role** has permissions to write to the S3 staging location used by Matillion
- Check CloudWatch logs for specific permission denial messages

---

## Detection Logic

Flag when any of the following are true:
- A pipeline contains a **Salesforce Query** or **Salesforce Load** component
- The component uses OAuth or token-based authentication
- The component runs inside an **iterator**
- The component extracts >50K records (API type selection matters)
- The pipeline was migrated from METL (Salesforce Query imports automatically; upgrade to Salesforce Load for Snowflake)
- The target environment uses a Customer-Hosted Agent (CHA)
- The target platform is Snowflake (Salesforce Query is deprecated; must use Salesforce Load)

## Remediation Decision Tree

```
Salesforce Component Detected
│
├─ Is the component greyed out or missing?
│  → Check agent version and manifest configuration
│  → For CHA: verify component availability by cloud/warehouse
│
├─ Is authentication failing?
│  → Verify Connected App grant types
│  → Check if Username-Password flow is disabled in Salesforce org
│  → Ensure Refresh Token scope is included
│
├─ Are row counts inconsistent?
│  → Test outside iterator first
│  → Switch to key-field validation (not count-based)
│  → Check QueryAll vs Query setting
│
├─ Is the extract >50K records?
│  → Switch to Bulk API 2.0
│  → Monitor API governor limits
│
├─ Are soft-deleted/archived records needed?
│  → Explicitly set QueryAll in component config
│
└─ Did column names change after migration/upgrade?
   → Validate output casing
   → Add explicit aliases in downstream SQL
```

## Priority Summary

| Category | Severity | Priority |
|----------|----------|----------|
| OAuth / token auth failures | 🔴 Critical | Verify Connected App config pre-execution |
| Component greyed out / version updates | 🔴 Critical | Set governance expectations; check agent version |
| Deprecation confusion (Query vs Load) | 🔴 Critical | Salesforce Load for Snowflake; Query for Databricks/Redshift |
| Inconsistent row counts (iterator context) | 🟠 High | Test in isolation; use key-field validation |
| API type selection (Bulk vs REST) | 🟠 High | Bulk API 2.0 for >50K records |
| QueryAll / archived records | 🟠 High | Explicitly verify setting; silent data loss risk |
| Column casing changes | 🟡 Medium | Validate output after migration/upgrade |
| IN comparator bug | 🟡 Medium | Use SOQL custom query as workaround |
| AWS access error (CHA) | 🟡 Medium | Verify IAM role for S3 staging bucket |