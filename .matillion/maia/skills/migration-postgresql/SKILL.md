---
name: migration-postgresql
description: PostgreSQL connector gotchas, driver behaviour, JSONB handling, case-sensitivity, and METL internal DB upgrade guidance during Matillion ETL to DPC migration.
---

# Migration PostgreSQL Connectors

## When to Use
- When migrating pipelines that extract from or load into PostgreSQL databases
- When upgrading the METL internal PostgreSQL metadata database (RDS)
- When PostgreSQL JSONB data is truncated during extraction
- When blank/NULL handling causes data integrity issues in PostgreSQL Load
- When column case-sensitivity issues appear after loading PostgreSQL data into Snowflake
- When pg_hba.conf authentication failures block DPC agent connections

## Why This Matters
PostgreSQL spans two completely different contexts in Matillion — as a **data pipeline source/target** and as METL's **internal metadata database**. Conflating these causes confusion for both customers and support. Driver behaviour changes between METL versions, JSONB type mapping, and case-sensitivity gotchas make PostgreSQL a high-touch connector during migration.

---

## Critical Context: Two Separate "PostgreSQL" Scenarios

| Context | Description | Components | Who Manages |
|---------|-------------|------------|-------------|
| **A — Pipeline Source/Target** | Extracting from or loading into a PostgreSQL database as part of a data pipeline | Database Query, PostgreSQL Query, PostgreSQL Load, RDS Bulk Output | Migration team / Data engineers |
| **B — METL Internal Metadata DB** | PostgreSQL instance that stores METL's own configuration and metadata (typically AWS RDS) | N/A — infrastructure only | Customer infra / DBA team |

> **Always clarify which context** before troubleshooting. Most PostgreSQL version/upgrade cases are Context B (infrastructure), not data pipeline issues.

---

## Gotcha #1 — PostgreSQL RDS Version EOL and METL Compatibility (Context B)

**Severity: 🔴 Critical**

The highest sustained case volume for PostgreSQL in 2025–2026.

### Symptom
Customers receive AWS notifications that their RDS PostgreSQL version (typically 13) is reaching end of standard support and need to know if METL supports newer versions.

### Key Facts
- METL v1.78 LTS supports **PostgreSQL 13 and 14** for the internal metadata DB
- PostgreSQL 17 support was **not confirmed** as of early 2026 — check current documentation
- In-place RDS upgrades from 13→14 are generally supported
- Upgrades to 16+ require testing against the specific METL version

### Remediation
- Check METL release notes for confirmed PostgreSQL version support before upgrading
- **Drop unused replication slots before upgrading** (see Gotcha #9)
- Test the upgrade in a non-production environment first

---

## Gotcha #2 — JSONB Data Truncated to VARCHAR(MAX) (Context A)

**Severity: 🔴 Critical**

### Symptom
PostgreSQL `jsonb` columns are truncated when extracted via the Database Query component. Large JSON documents lose data.

### Root Cause
The JDBC driver doesn't natively understand `jsonb` as a type — it falls back to `varchar`, which may truncate on the target warehouse.

### Remediation
- Cast jsonb columns explicitly in the SQL query:
  ```sql
  SELECT column_name::text FROM my_table
  -- or
  SELECT CAST(column_name AS TEXT) FROM my_table
  ```
- Be aware of downstream column type implications in Snowflake/Redshift
- Validate JSON document completeness after extraction

---

## Gotcha #3 — BLANK Values Set as NULL in PostgreSQL Load (Context A)

**Severity: 🟠 High**

### Symptom
When loading data into a PostgreSQL target, empty string values (`''`) are written as `NULL`.

### Root Cause
A well-known JDBC/PostgreSQL interaction — some drivers and PostgreSQL configurations treat empty strings differently from NULL.

### Remediation
- Use a `NULLIF` or `COALESCE` transformation step upstream to explicitly handle the blank/null distinction before load
- Validate data integrity in the PostgreSQL target after initial loads

---

## Gotcha #4 — RDS Bulk Output vs PostgreSQL Load Compatibility (Context A)

**Severity: 🟠 High**

Two components can write to Amazon RDS PostgreSQL, with different behaviours:

| Component | Mechanism | Best For | Gotchas |
|-----------|-----------|----------|--------|
| **RDS Bulk Output** | S3 staging → COPY | Large batch loads | Cast/NULL handling edge cases when source schema doesn't perfectly map to target |
| **PostgreSQL Load** | Direct JDBC | Smaller/medium loads | BLANK→NULL issue (Gotcha #3); may not be natively optimised for RDS |

### Remediation
- Always validate data type mapping between source and PostgreSQL target before bulk loads
- For Amazon RDS PostgreSQL targets, test both components to determine which handles your schema correctly

---

## Gotcha #5 — Double-Quoting Field Names / Case-Sensitivity (Context A)

**Severity: 🟠 High**

### Symptom
The Database Query component double-quotes PostgreSQL column names. When loaded into Snowflake, these create **case-sensitive column names**, breaking downstream queries that expect uppercase.

### Example
PostgreSQL column `myColumn` → extracted as `"myColumn"` → lands in Snowflake as case-sensitive `myColumn` instead of `MYCOLUMN`.

### Remediation

| Option | Details |
|--------|---------|
| **Alias columns in SQL** | `SELECT my_column AS MY_COLUMN` — force uppercase on extraction |
| **Snowflake session parameter** | Set `QUOTED_IDENTIFIERS_IGNORE_CASE = TRUE` |
| **Column mapping** | Use component column mapping to rename on ingest |

---

## Gotcha #6 — Driver Behaviour Change Between METL 1.68 and 1.78 (Context A)

**Severity: 🟠 High**

### Symptom
Observable performance and behaviour differences in the Bulk Output component writing to PostgreSQL targets after upgrading from METL 1.68 to 1.78.

### Root Cause
The PostgreSQL JDBC driver bundled with METL changed between versions, altering batch write behaviour.

### Remediation
- Treat 1.68→1.78 PostgreSQL driver changes as a **known migration risk** for customers using PostgreSQL as a target
- Connection options that may help:
  - `reWriteBatchedInserts=true` — significantly improves batch insert performance
  - Increase batch size in component settings
- Benchmark write performance before and after upgrade

---

## Gotcha #7 — pg_hba.conf Authentication Failures (Context A)

**Severity: 🟡 Medium**

### Symptom
```
FATAL: no pg_hba.conf entry for host "x.x.x.x", user "y", database "z"
```

### Root Cause
The PostgreSQL server rejects the connection because the DPC/METL agent's IP isn't in `pg_hba.conf`. Common with on-prem or self-managed PostgreSQL instances.

### Remediation
- **DPC Full SaaS:** Add Matillion's egress IP range to `pg_hba.conf`
- **Hybrid agents:** Agent IP may change on restart — use CIDR range or assign a static IP
- This is a **customer infrastructure action** — track as a customer action item

---

## Gotcha #8 — Date Filter Type Mismatch in Database Query (Context A)

**Severity: 🟡 Medium**

Date parameters passed to the Database Query component don't always cast correctly against PostgreSQL date/timestamp columns. The JDBC driver interprets date types differently depending on whether `DATE`, `TIMESTAMP`, or string literals are used.

### Remediation
- Cast date filters explicitly in SQL: use `TO_DATE()` or `TIMESTAMP` literals rather than raw string variables
- Test date filtering in isolation before embedding in complex queries

---

## Gotcha #9 — Replication Slot Failures After PostgreSQL Upgrade (Context B)

**Severity: 🟡 Medium**

### Symptom
After upgrading the METL internal PostgreSQL metadata DB (e.g., RDS in-place upgrade), replication slots left behind cause post-upgrade failures or disk space issues.

### Remediation
- **Before upgrading**, drop unused replication slots:
  ```sql
  -- Check for active slots
  SELECT * FROM pg_replication_slots;
  -- Drop unused slots
  SELECT pg_drop_replication_slot('slot_name');
  ```
- Replication slots prevent WAL cleanup and can cause disk exhaustion

---

## Gotcha #10 — Large-Scale PostgreSQL to Snowflake Migration (Context A)

**Severity: 🟡 Medium**

For very large PostgreSQL databases (10TB+), the Database Query component pulls all data into memory/staging with **no native streaming** for very large tables.

### Design Recommendations
- Use **incremental load patterns** with date-based chunking
- Design parallel pipeline strands for different table partitions
- Size the agent appropriately — larger tables require more agent RAM headroom
- Consider **CDC-based replication** for ongoing sync at scale rather than batch Database Query

---

## Detection Logic

Flag when any of the following are true:
- A pipeline contains a **Database Query** component with a PostgreSQL JDBC connection
- A pipeline contains a **PostgreSQL Query** or **PostgreSQL Load** component
- The pipeline extracts `jsonb` columns from PostgreSQL
- The pipeline loads data into a PostgreSQL/RDS target
- The METL instance uses RDS PostgreSQL 13 or earlier for its internal DB
- Column names from PostgreSQL are case-mixed (not all uppercase)
- The customer is upgrading METL versions (1.68→1.78 or later)

## Remediation Decision Tree

```
PostgreSQL Issue Detected
│
├─ Which context?
│  ├─ Context A (Pipeline source/target) → Continue below
│  └─ Context B (METL internal DB) → Version compatibility / upgrade path
│
├─ Is data being truncated?
│  → JSONB columns? Cast to TEXT in SQL query
│
├─ Are blanks becoming NULL?
│  → Add NULLIF/COALESCE upstream of PostgreSQL Load
│
├─ Are column names case-sensitive in Snowflake?
│  → Alias to uppercase in SQL or set QUOTED_IDENTIFIERS_IGNORE_CASE
│
├─ Is the connection being rejected?
│  → pg_hba.conf: whitelist agent IP/CIDR
│
├─ Is write performance degraded after METL upgrade?
│  → Set reWriteBatchedInserts=true; benchmark batch size
│
└─ Is this a large-scale migration (10TB+)?
   → Incremental date-based chunking
   → Consider CDC for ongoing replication
```

## Priority Summary

| Category | Severity | Context | Priority |
|----------|----------|---------|----------|
| RDS PostgreSQL version EOL / METL compatibility | 🔴 Critical | B | Check before any RDS upgrade |
| JSONB truncation to VARCHAR(MAX) | 🔴 Critical | A | Cast to TEXT in extraction SQL |
| BLANK→NULL in PostgreSQL Load | 🟠 High | A | Add upstream null handling |
| RDS Bulk Output vs PostgreSQL Load | 🟠 High | A | Test both; validate type mapping |
| Double-quoting / case-sensitivity | 🟠 High | A | Alias columns or set Snowflake session param |
| Driver behaviour change (1.68→1.78) | 🟠 High | A | Set reWriteBatchedInserts; benchmark |
| pg_hba.conf auth failures | 🟡 Medium | A | Customer infra action: whitelist agent IP |
| Date filter type mismatch | 🟡 Medium | A | Cast dates explicitly in SQL |
| Replication slot failures after upgrade | 🟡 Medium | B | Drop unused slots before upgrade |
| Large-scale migration design | 🟡 Medium | A | Incremental chunking; consider CDC |