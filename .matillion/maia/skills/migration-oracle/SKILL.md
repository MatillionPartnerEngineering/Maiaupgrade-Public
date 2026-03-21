---
name: migration-database-query-oracle
description: Oracle-specific gotchas, performance tuning, and migration patterns for Database Query components during Matillion ETL to DPC migration. Covers fetch size, large table handling, data integrity, authentication, and the strategic shift toward native Oracle components.
---

# Migration Database Query — Oracle

## When to Use
- When migrating Database Query components that extract from Oracle sources
- When Oracle extractions run significantly slower on DPC than METL
- When Database Query components hang or get stuck on large Oracle tables
- When Oracle authentication (Wallet, encrypted private key) fails after migration
- When data integrity issues (duplicates, excess records) appear after Oracle extraction

## Why This Matters
Oracle extractions are the most frequently reported performance and reliability issue during METL → DPC migration. Fetch size tuning, which is critical for Oracle specifically, is **not configurable** in DPC's Database Query component — a key behavioral difference from METL that can cause 10x+ slowdowns on large tables.

## Strategic Direction

> **Important:** Matillion is moving away from the Database Query component as more RDBMS-specific components are added. The **Oracle Load** component is the forward-looking path for Oracle → Snowflake extractions. It includes a native **Fetch Size** property and supports both **Full Load** and **Incremental Load** (high-water mark based).

When advising on Oracle migration to Snowflake, prefer the Oracle Load component over Database Query.

### Oracle Load Component — Key Details

| Property | Details |
|----------|---------|
| **Availability** | Snowflake only (not Databricks or Redshift) |
| **Auth** | Username & Password (via secret reference) |
| **Connection URL** | `jdbc:oracle:thin:@<host>:<port>/<database>` |
| **Load Type** | Full Load or Incremental Load |
| **Mode** | Basic (visual) or Advanced (SQL query) |
| **Fetch Size** | Native property in Advanced Settings — set explicitly for large tables |
| **Load Strategy** | Replace, Truncate and Insert, Fail if Exists, Append |
| **Incremental** | High-water mark based; supports merge via Primary Keys |
| **SSH Tunnel** | Supported natively |
| **Staging** | S3, Snowflake internal, Azure Storage, or GCS |

### Migration Path: Database Query (Oracle) → Oracle Load

The Oracle Load component is **not a drop-in replacement** — it requires manual reconfiguration:

| Database Query Property | Oracle Load Equivalent |
|------------------------|----------------------|
| Source (Oracle) | Connection URL (`jdbc:oracle:thin:@host:port/db`) |
| Username / Password | Username / Password (secret reference) |
| SQL Query | SQL Query (Advanced mode) or Data Source + Filters (Basic mode) |
| Target Table | Table Name (under Destination) |
| Database / Schema / Warehouse | Same properties under Destination |
| Connection Options | Connection Options (JDBC parameters) |
| Fetch Size (METL) | **Fetch Size** (Advanced Settings) — carry forward the METL value |
| RECREATE TARGET TABLE | Load Strategy → Replace |
| N/A (new capability) | **Incremental Load** with high-water mark |

> **Key advantage:** Oracle Load's native Fetch Size property eliminates the #1 Oracle performance issue during migration. Always set this explicitly for large table extractions.

---

## Gotcha #1 — Fetch Size Must Be Configured for Oracle Performance

**Severity: 🔴 Critical**

This is the #1 Oracle performance issue during migration.

### Symptom
Oracle extractions that ran in minutes on METL take 10-15x longer on DPC when fetch size is not explicitly configured (e.g., 7 minutes → 1 hour 47 minutes).

### Root Cause
Oracle's default fetch size is very small. On METL, `fetchsize` was often tuned to large values (e.g., 100,000). If this tuning is not carried forward to DPC, extractions fall back to the driver default, causing severe performance degradation.

### Remediation
Fetch size **can and should** be explicitly configured in DPC for Oracle extractions:

| Option | Details |
|--------|---------|
| **Oracle Load component** (Recommended) | Has a native **Fetch Size** property in Advanced Settings. See migration path table above for property mapping. |
| **Database Query component** | Set fetch size via connection options or component configuration |
| **JDBC component** | Supports a manifest file where `fetchSize` can be configured |

### Migration Action
When migrating from METL, check if the source component had a custom `fetchsize` and ensure the same value is carried forward to the DPC component.

> **Key call-out:** Oracle is specifically the database where fetch size tuning matters most. For other databases, driver defaults are typically optimal.

---

## Gotcha #2 — Component Hangs on Large Oracle Tables

**Severity: 🔴 Critical**

The most frequently reported Oracle issue. The job doesn't fail cleanly — it hangs indefinitely.

### Pattern
Almost always correlates with large table volumes and no fetch size tuning.

### Recommended Approach
- Implement **incremental/delta loading** patterns rather than full table scans
- Use **query predicates** (WHERE clauses) to scope extracted data
- Set appropriate **job timeouts** and retry logic in the orchestration layer
- Switch to the **Oracle Load component** where fetch size can be explicitly controlled

---

## Gotcha #3 — Data Integrity Issues (Excess Records / Duplicates)

**Severity: 🟠 High**

Two dangerous patterns observed:

1. **More rows in target than source** — excess records loaded into Snowflake
2. **Row count matches but key metrics don't** — some rows dropped from source, others duplicated in target. This is particularly dangerous because count-based validation masks actual data corruption.

### Root Cause
Pagination behavior during Oracle extraction can cause rows to be duplicated or skipped, especially with large result sets.

### Recommendation
- **Count-based validation is insufficient** for Oracle extracts using pagination
- Use **checksum or key-metric validation** in addition to row counts
- Validate sample data with source-to-target column-level comparisons

---

## Gotcha #4 — Oracle Unload Requires CREATE TABLE Privileges

**Severity: 🟠 High**

### Symptom
```
Unable to stage data: Failed to create table: ORA-01031: insufficient privileges
```

### Root Cause
The Oracle Unload component **stages data in a temporary table first** before performing the update. This requires:
- **CREATE TABLE** privileges on the target Oracle schema
- Sufficient **tablespace quota** (`USER_TS_QUOTAS`)

### Key Detail
Standard privilege checks (`USER_SYS_PRIVS`, `USER_TAB_PRIVS`, `SESSION_PRIVS`) alone are insufficient — customers must also check `USER_TS_QUOTAS`.

---

## Gotcha #5 — Column Precision Not Respected with RECREATE TARGET TABLE

**Severity: 🟡 Medium**

When using **RECREATE TARGET TABLE**, the component may not honour original Oracle column precision (e.g., `NUMBER(18,4)` may land as `NUMBER` or a generic type).

### Recommendation
- Validate DDL of recreated tables post-load
- Use **Create/Replace Table** component to explicitly define target schema
- Or use a fixed target table structure with **TRUNCATE & INSERT** instead of recreate

---

## Gotcha #6 — Multiline Values in VARCHAR Fields Fail to Load

**Severity: 🟡 Medium**

Oracle text fields with embedded newlines (`\n`, `\r\n`) can cause parsing issues during extraction. This is a known edge case particularly for **CLOB** or long **VARCHAR2** columns.

> **Note:** Oracle CLOB datatype mapping in query-based replication is a documented known issue.

---

## Gotcha #7 — Hybrid Agent ECS Scaling Doesn't Improve Oracle Concurrency

**Severity: 🟡 Medium**

Scaling up ECS tasks on a DPC Hybrid Agent does **not automatically parallelise** Oracle extraction jobs. Job concurrency in DPC is governed differently than METL — particularly relevant during Oracle → Snowflake migration patterns.

Customers expecting METL-like concurrency behaviour should validate actual parallelism after scaling.

---

## Gotcha #8 — Authentication: Encrypted Private Key & Oracle Wallet

**Severity: 🟡 Medium**

Oracle Wallet authentication is a recurring migration issue. Key points:

- Oracle Wallet (`.p12` / `tnsnames.ora`) requires specific JDBC connection string formatting
- Agent-side CloudWatch logs are useful for debugging authentication failures
- Private key encryption adds complexity — ensure the key passphrase is correctly passed via connection options

---

## Detection Logic

Flag when any of the following are true:
- A **Database Query** component has `source: Oracle` or uses an Oracle JDBC URL
- The METL source had a custom `fetchsize` configured
- The extraction targets large tables (>1M rows)
- Oracle Wallet or encrypted private key authentication is in use
- The component uses **RECREATE TARGET TABLE** mode
- Oracle Unload components are present in the workload

## Remediation Decision Tree

```
Oracle Database Query Component Detected
│
├─ Was fetch size tuned on METL?
│  → YES → Carry forward the same value to DPC component
│  → Prefer Oracle Load component (native Fetch Size in Advanced Settings)
│  → Or configure via Database Query connection options / JDBC manifest
│
├─ Is the target platform Snowflake?
│  → YES → Consider migrating to Oracle Load component (see property mapping above)
│  → NO (Databricks/Redshift) → Oracle Load is not available; use Database Query or JDBC
│
├─ Is the table large (>1M rows)?
│  → Implement incremental/delta loading
│  → Add query predicates to scope extraction
│  → Set job timeout in orchestration
│
├─ Is RECREATE TARGET TABLE enabled?
│  → Validate target DDL precision post-load
│  → Consider fixed schema + TRUNCATE & INSERT
│
├─ Is Oracle Unload present?
│  → Verify CREATE TABLE privilege
│  → Verify tablespace quota (USER_TS_QUOTAS)
│
└─ Is Wallet / private key auth in use?
   → Verify JDBC connection string format
   → Check agent CloudWatch logs for auth errors
```

## Priority Summary

| Category | Severity | Priority |
|----------|----------|----------|
| Fetch size not carried forward from METL | 🔴 Critical | Detect and configure before first execution |
| Component hanging on large tables | 🔴 Critical | Implement incremental loading or Oracle Load |
| Data integrity / duplicate rows | 🟠 High | Add key-metric validation beyond row counts |
| Oracle Unload permissions | 🟠 High | Verify privileges pre-execution |
| Column precision with RECREATE TABLE | 🟡 Medium | Validate DDL post-load |
| Multiline / CLOB fields | 🟡 Medium | Manual review of text-heavy columns |
| ECS concurrency for Oracle | 🟡 Medium | Set expectations; validate parallelism |
| Authentication (Wallet / Private Key) | 🟡 Medium | Verify connection string and agent logs |