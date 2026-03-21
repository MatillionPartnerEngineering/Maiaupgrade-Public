---
name: migration-netsuite
description: NetSuite connector gotchas, authentication patterns, driver management, and performance tuning for Database Query (SuiteAnalytics JDBC), NetSuite Query, and NetSuite SuiteAnalytics components during Matillion ETL to DPC migration.
---

# Migration NetSuite Connectors

## When to Use
- When migrating pipelines that extract data from NetSuite
- When NetSuite authentication (OAuth, Token, JDBC RTK) fails after migration or instance change
- When Database Query components hang on large NetSuite tables (e.g., transactionLine)
- When NetSuite columns are missing from query results (custom segments, role-dependent fields)
- When upgrading METL instances or refreshing AMIs that use NetSuite JDBC/ODBC drivers

## Why This Matters
NetSuite is one of the highest-volume connector categories across the entire support case history. Authentication and driver setup account for the majority of issues. The connector landscape spans three distinct approaches, each with different failure modes — making this a complex migration target.

---

## The Three Connector Paths

Customers connect to NetSuite via three distinct approaches. Understanding which path a customer uses is **essential** before troubleshooting.

| # | Approach | Platform | Auth Method | Best For |
|---|---------|----------|-------------|----------|
| 1 | **Database Query + SuiteAnalytics Connect JDBC driver** | METL (still active in DPC via JDBC) | Token Password or JDBC RTK key | Legacy METL pipelines; bulk extraction via JDBC |
| 2 | **NetSuite Query component** | DPC | OAuth / SuiteQL | Modern SuiteQL queries; better schema resolution for custom fields |
| 3 | **NetSuite SuiteAnalytics component** | DPC | OAuth 2.0 (M2M / Client Credentials) | Native DPC connector; OAuth-based |

### Migration Guidance
- **METL → DPC (Snowflake):** Database Query components with NetSuite JDBC will import but may need driver re-upload (Hybrid SaaS) or migration to the native NetSuite Query/SuiteAnalytics components
- **New DPC pipelines:** Prefer the **NetSuite Query** or **NetSuite SuiteAnalytics** components over Database Query + JDBC
- **Custom segments (cseg_*):** If the pipeline relies on custom segment columns, the NetSuite Query component with SuiteQL provides better schema resolution than JDBC

---

## Gotcha #1 — CData RTK Key Is Per-Instance and Non-Transferable (METL)

**Severity: 🔴 Critical**

The most operationally disruptive NetSuite gotcha for METL customers.

### Symptom
NetSuite extractions fail immediately after an instance replacement, AMI refresh, or METL version upgrade.

### Root Cause
- The SuiteAnalytics Connect JDBC driver requires a **CData RTK (Runtime Key)** licensed per-instance
- When customers spin up new EC2 instances, restore from AMIs, or upgrade METL versions, the driver key needs to be **re-applied or re-acquired**
- Post-AMI refresh, pyodbc and ODBC driver configs can be **wiped entirely**, causing silent failures

### Remediation
- RTK keys must be **re-entered after any instance replacement**
- ODBC driver installation must be **re-run post-AMI refresh** — it is not persisted automatically
- Customers upgrading across major METL versions have a specific driver re-installation procedure

> **Diagnostic anchor:** Always ask *"When did this stop working?"* — if the answer is "after an upgrade or new instance," the RTK/ODBC driver is almost certainly the culprit.

---

## Gotcha #2 — OAuth Authentication Failures (Multiple Root Causes)

**Severity: 🔴 Critical**

The #1 DPC-era NetSuite gotcha with the most complex failure tree.

### The Four Root Causes (in order of frequency)

#### A) Sandbox Account ID Format Mismatch
- NetSuite sandbox accounts have IDs in two formats: `xxxxx_sb1` (underscore) and `xxxxx-sb1` (hyphen)
- **UI login context** expects: `xxxxx_sb1`
- **SuiteAnalytics Connect driver / realm context** expects: `xxxxx-sb1`
- DPC may not correctly parse the sandbox realm format
- **Fix:** Try both formats; confirm which context requires which format

#### B) Wrong OAuth Grant Type
- SuiteAnalytics Connect typically uses **Machine-to-Machine (M2M / Client Credentials)**
- If the DPC connector is configured for **Authorization Code** flow instead, the token exchange fails silently with a generic 500 error
- **Fix:** Confirm the NetSuite integration record is set up for Client Credentials, not Auth Code

#### C) Secrets Manager Entry Deleted or Rotated
- Deleting the cloud secrets manager entry (e.g., AWS Secrets Manager) breaks the OAuth token refresh silently
- **Fix:** Never delete secrets manager entries without re-creating the connection profile in DPC

#### D) Sandbox Refresh Breaks Credentials
- After a NetSuite sandbox refresh: integration/app IDs change, roles/permissions differ, credentials rotate
- Manifests as *"token retrieval failed"* even when configuration looks correct
- **Fix:** After any sandbox refresh, re-authorise the integration record and verify role/scope assignments

### Authentication Decision Tree

```
NetSuite Auth Failure
│
├─ Is this a sandbox account?
│  → Try both ID formats: xxxxx_sb1 and xxxxx-sb1
│  → Was the sandbox recently refreshed? Re-authorise integration record
│
├─ Is the grant type correct?
│  → SuiteAnalytics: Client Credentials (M2M)
│  → NOT Authorization Code
│
├─ Was a secrets manager entry recently deleted/rotated?
│  → Re-create connection profile in DPC
│
└─ Is this METL with Token Password auth?
   → Verify token is valid and not expired
   → Check JDBC connection string for correct auth parameters
```

---

## Gotcha #3 — Database Query Hangs on Large NetSuite Tables

**Severity: 🔴 Critical**

The most persistent performance gotcha — affects both METL and DPC.

### Pattern
- The `transactionLine`, `transaction`, and other high-volume NetSuite objects are notoriously large and poorly indexed for bulk extraction
- Queries that work on smaller tables stall on these objects
- JDBC/ODBC timeout defaults are often too short for large NetSuite extractions
- NetSuite enforces **API concurrency limits per account** — concurrent extractions compound the problem

### Optimisation Strategies

| Strategy | Details |
|----------|---------|
| **Narrow the date window** | Use `date_last_modified_gmt` with tight incremental windows rather than full reloads |
| **Reduce column count** | Avoid `SELECT *`; NetSuite returns many nullable/calculated columns that inflate payload |
| **Switch to SuiteQL** | The native NetSuite Query component is more performant for large tables than JDBC |
| **Increase JDBC timeout** | Set connection timeout explicitly in the driver connection string |
| **Avoid concurrent extractions** | NetSuite enforces API concurrency limits per account; schedule sequentially |
| **Set fetch size** | If using Database Query, configure fetch size via connection options for large result sets |

---

## Gotcha #4 — Missing Columns in NetSuite Query Results

**Severity: 🟠 High**

### Symptom
Columns visible via the NetSuite REST API or Postman are missing from Matillion query results. Common with custom segments (`cseg_*`) and role-dependent fields like `department`.

### Root Cause
- The JDBC driver uses a **fixed/cached schema** for some tables — custom segments and certain role-dependent fields may not appear in the driver's metadata
- Null values on fields that are populated in the NetSuite UI indicate a permissions/role issue on the integration record

### Remediation

| Scenario | Fix |
|----------|-----|
| Custom segment columns (`cseg_*`) missing | Use **SuiteQL via NetSuite Query component** (more dynamic schema resolution) or **NetSuite REST API via Python** |
| Standard field missing (e.g., `department`) | Check permissions/role on the NetSuite integration record |
| Fields present but null | Verify the integration role has field-level access in NetSuite |

---

## Gotcha #5 — Date Filter Type Mismatch (Database Query + SuiteAnalytics)

**Severity: 🟠 High**

### Symptom
Date parameters passed to the Database Query component don't cast correctly against NetSuite's SuiteAnalytics date columns. The JDBC driver interprets date types differently depending on whether `DATE`, `TIMESTAMP`, or string literals are used.

### Known Issue
The `deletedrecord` table's `deleteddate` column causes query failure if included in the SELECT — works via API but errors in the component.

### Remediation
- Cast date filters explicitly: use `TO_DATE()` or `TIMESTAMP` literals rather than passing raw string variables
- For the `deletedrecord` table, exclude `deleteddate` from the SELECT and retrieve it separately if required

---

## Gotcha #6 — SuiteAnalytics Component Slow Validation / Validation Hang

**Severity: 🟡 Medium**

### Symptom
The NetSuite SuiteAnalytics component takes minutes to hours to validate, or validation hangs indefinitely.

### Root Cause
The component makes a metadata call to NetSuite during validation to enumerate available tables/fields. For accounts with many custom objects, custom segments, or large schemas, this can be extremely slow. Scheduled pipelines can time out during this validation step.

### Remediation
- Disable auto-validation in Designer for NetSuite components where possible
- Pre-validate during development, not at runtime
- Avoid putting validation-heavy NetSuite components in high-frequency scheduled pipelines

---

## Gotcha #7 — Commas in Data Causing Column Splits (Hybrid JDBC)

**Severity: 🟡 Medium**

The hybrid NetSuite JDBC adaptor handles string fields containing commas incorrectly in some configurations. Fields like free-text address lines, memos, or item descriptions that contain commas get split across columns.

### Remediation
- Ensure the JDBC driver is configured to **quote string fields** — check the connection string for quoting options
- Apply string cleaning in the SQL query: `REPLACE(field, ',', '')` as a workaround
- This is a known driver-layer issue — raise with support if driver-level quoting cannot be configured

---

## Detection Logic

Flag when any of the following are true:
- A pipeline contains a **Database Query** component with a NetSuite JDBC/ODBC connection
- A pipeline contains a **NetSuite Query** or **NetSuite SuiteAnalytics** component
- The component extracts from high-volume NetSuite objects (`transactionLine`, `transaction`)
- OAuth or Token Password authentication is configured
- The METL instance was recently upgraded, refreshed from AMI, or replaced
- The pipeline targets a NetSuite sandbox account
- Custom segment columns (`cseg_*`) are expected in the output

## Remediation Decision Tree

```
NetSuite Component Detected
│
├─ Which connector path?
│  ├─ Database Query + JDBC → Check RTK key, driver version, fetch size
│  ├─ NetSuite Query (SuiteQL) → Check OAuth grant type, sandbox ID format
│  └─ NetSuite SuiteAnalytics → Check OAuth M2M config, validation performance
│
├─ Is auth failing?
│  → Follow Authentication Decision Tree (Gotcha #2)
│
├─ Is the component hanging on large tables?
│  → Narrow date window, reduce columns, consider SuiteQL
│  → Check API concurrency limits
│
├─ Are columns missing?
│  → Custom segments? Use SuiteQL or REST API
│  → Standard fields? Check integration role permissions
│
├─ Was the instance recently replaced/upgraded? (METL)
│  → Re-enter RTK key
│  → Re-install ODBC driver
│
└─ Is this a sandbox?
   → Verify account ID format (underscore vs hyphen)
   → After refresh: re-authorise integration record
```

## Priority Summary

| Category | Severity | Priority |
|----------|----------|----------|
| CData RTK key / driver install (METL) | 🔴 Critical | Verify immediately after any instance change |
| OAuth authentication failures | 🔴 Critical | Follow 4-cause decision tree |
| Hanging on large tables | 🔴 Critical | Implement incremental extraction; consider SuiteQL |
| Missing columns / custom segments | 🟠 High | Use SuiteQL or verify integration role permissions |
| Date filter type mismatch | 🟠 High | Cast dates explicitly; special handling for deletedrecord |
| Slow validation / validation hang | 🟡 Medium | Disable auto-validation; pre-validate in development |
| Commas in data (JDBC) | 🟡 Medium | Configure driver quoting or apply string cleaning |