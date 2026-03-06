---
name: migration-connectors
description: Use when refactoring Database Query, JDBC, dbt, or other connector components during Matillion ETL to DPC migration.
---

# Connectors Migration Guide

## Database Query Migration

Reference: https://docs.matillion.com/metl/docs/migration-database-query/

DPC has an equivalent **Database Query** component but vendor restrictions prevent shipping all drivers.

### Automatically Upgraded Sources

These migrate without manual intervention:
- Amazon Redshift
- IBM DB2 for i
- MariaDB
- Microsoft SQL Server
- Oracle
- PostgreSQL
- Sybase ASE
- Snowflake
- SQL Server (Microsoft driver)

### Sources Requiring Driver Upload (Hybrid SaaS Only)

If source not supported by default:
1. Component automatically changed to **JDBC**
2. Properties configured where possible
3. **You must:**
   - Upload a suitable JDBC driver for each source
   - Create a **manifest file** per JDBC component documentation

### MySQL Special Case

DPC can't ship the official MySQL driver.
- Uses **MariaDB driver** (compatible)
- MySQL components are changed to use MariaDB driver during migration
- If you need the official MySQL driver:
  - Use JDBC and provide your own driver

---

## dbt Migration

Reference: https://docs.matillion.com/metl/docs/migration-dbt/

dbt is supported in DPC. Jobs using **Commands for dbt Core** can migrate but require manual changes.

### Key Difference

| Platform | Git Sync Method |
|----------|----------------|
| Matillion ETL | **Sync File Source** component |
| DPC | Built into **dbt Core** component |

### Upgrade Path

#### Before Migration (Matillion ETL)

1. Inspect **Sync File Source** and note the **External File Source**
2. Open **Project → Manage External File Sources**
3. Note these settings:
   - Remote URL
   - Username
   - Password
   - Branch

#### After Migration (DPC)

1. Open migrated pipeline in DPC Designer
2. **Sync File Source** becomes **Unknown Component**:
   - Delete it
   - Reconnect components around it
3. In **dbt Core** properties:
   - Set **dbt Project Location = External repository**
4. Configure using noted settings:

| Sync File Source | dbt Core |
|------------------|----------|
| Remote URL | Git URL |
| Username | Git Username |
| Password | Git Password (store in secret) |
| Branch | Git Branch |

> **Tip:** If multiple pipelines share config, use **project variables**.

### dbt Version Compatibility

To avoid issues, ensure Matillion ETL runs the same dbt version as DPC before migration.

- DPC runs most recent stable dbt (updates periodically)
- You can't manually change dbt version in DPC

**Recommended Matillion ETL upgrade command:**
```bash
python3 -m pip install dbt-core dbt-postgres dbt-redshift dbt-snowflake dbt-bigquery
```

---

## Temporary Tables

Reference: https://docs.matillion.com/metl/docs/migration-temporary-tables/

Due to DPC's distributed nature, **temporary tables cannot be supported**.
- Temporary tables exist only in the session that created them
- DPC creates multiple sessions for parallelism

### Upgrade Path

Refactor to use:

| Warehouse | Alternative |
|-----------|-------------|
| Snowflake | **Transient tables** |
| Databricks | **Permanent tables** |
| Amazon Redshift | **Permanent tables** |

---

## Transactions

Reference: https://docs.matillion.com/metl/docs/migration-transactions/

DPC supports **Begin**, **Commit**, and **Rollback** transaction components.

### Key Difference

| Platform | Components in Transaction |
|----------|---------------------------|
| Matillion ETL | Any component |
| DPC | Only **Run Transform** and **SQL Script** |

> **Warning:** DDL in SQL Script forces commit.

Other components run outside the transaction without error.

### Upgrade Path

Transactions migrate automatically. If jobs relied on DDL behavior forcing commits within transactions, refactor as this is no longer permitted.

---

## Replicate Components

Reference: https://docs.matillion.com/metl/docs/migration-replicate/

The **Replicate** component isn't needed in DPC — all components have multiple outputs by default.

### Upgrade Path

- Replicate components are **automatically removed** during migration
- Connections previously routed through Replicate are established directly
- **No manual intervention required**
