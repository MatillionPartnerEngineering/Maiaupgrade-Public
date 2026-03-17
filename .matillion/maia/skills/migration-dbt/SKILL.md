# Upgrade: dbt

Reference: https://docs.matillion.com/metl/docs/migration-dbt/

dbt is supported by DPC. Matillion ETL jobs using **Commands for dbt Core** can be migrated and continue to run as expected, but manual changes are required to connect to a Git repository.

Key difference:

- Matillion ETL uses **Sync File Source** to fetch latest dbt files from Git.
- In DPC, file sync is done inside the **dbt Core** component, so Sync File Source is unnecessary.

## Upgrade path

Before migrating (Matillion ETL):

1. Inspect **Sync File Source** and note the **External File Source**.
2. Open **Project → Manage External File Sources**.
3. Select the file source and note:
   - Remote URL
   - Username
   - Password
   - Branch

After upgrade (DPC):

1. Open migrated pipeline in DPC Designer.
2. Sync File Source becomes **Unknown Component**:
   - Delete it and reconnect components around it.
3. In **dbt Core** properties:
   - Set **dbt Project Location = External repository**
4. Configure dbt Core using noted settings:

| Sync File Source property | dbt Core property |
|---|---|
| Remote URL | Git URL |
| Username | Git Username |
| Password | Git Password (store in a secret definition) |
| Branch | Git Branch |

If multiple pipelines share config, consider using **project variables**.

> **Note**  
> In DPC, repository configuration in dbt Core is required. If you have no values to copy, create values per dbt Core documentation.

## dbt versions

To avoid issues, ensure Matillion ETL is running the same dbt version as DPC before migration.

- DPC runs the most recent stable dbt and updates periodically.
- Matillion ETL dbt version can lag based on your upgrade cadence.

> **Note**  
> You can’t manually change dbt version in DPC.

Recommended Matillion ETL upgrade command:

```bash
python3 -m pip install dbt-core dbt-postgres dbt-redshift dbt-snowflake dbt-bigquery
```