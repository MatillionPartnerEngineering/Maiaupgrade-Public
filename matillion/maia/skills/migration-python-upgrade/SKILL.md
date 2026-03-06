---
name: migration-python-upgrade
description: Use when refactoring Python Script, Python 2, Jython, or Python Pushdown components during Matillion ETL to DPC migration.
---

# Python Migration Upgrade Guide

Reference: https://docs.matillion.com/metl/docs/migration-python/

## Overview

DPC includes a **Python Script** component but also offers alternatives:
- Native components (Print Variables, Move File, Delete File, Send Email)
- **Python Pushdown** (Snowflake only)
- **Bash Pushdown** with Python execution

## Key Differences from Matillion ETL

| Aspect | Matillion ETL | DPC |
|--------|---------------|-----|
| Runtime | Linux VM with persistent disk | SaaS containers (no persistence) |
| Python versions | Python 2, Python 3, Jython | **Python 3 only** (currently 3.10) |
| Package installation | pip/apt available | Immutable filesystem |
| Compute resources | VM-sized | Lower CPU/memory (not for intensive ops) |
| Deployment | Any | **Hybrid SaaS only** for Python Script |

## Upgrade Path (Recommended Order)

### 1. Replace with Native Components
Check if functionality has a native component equivalent:
- Print Variables
- Move File
- Delete File
- Send Email with Attachment

### 2. Python Pushdown (Snowflake Only)
**Advantages:**
- Runs on scalable Snowflake warehouses
- Direct access to Snowflake database connections
- Designed for heavy processing (including pandas)
- Full access to DPC variables
- Many packages accessible by default
- Can be secured with network access control

**Considerations:**
- May require Python refactoring
- Requires initial Snowflake account setup
- Requires network access configuration
- Snowflake projects only

### 3. Python Script Component (Hybrid SaaS Only)
- Refactor to avoid filesystem reliance
- Python 3 only
- Limited CPU/memory

### 4. Bash Pushdown Alternative
Run Python scripts on your own Linux machine via SSH.
- Full control over CPU/memory
- Install any packages
- You must manage the machine

---

## Converting Python 2 to Python 3

DPC supports Python 3 only. Migration tool auto-converts using `2to3`.

### Steps
1. Click **Edit preferences** in **Importing files** panel
2. Toggle **Convert Python 2.x to 3** to **On**
3. Click **Apply & re-run**
4. Report shows: "Your Python script has been auto-converted using the 2to3 tool."
5. Click **Import**

**After conversion:**
- Both versions stored at: `.matillion → migration → <date> → <pipeline>`
- Files named `_before` and `_after`
- Review and test thoroughly — `2to3` doesn't guarantee correctness

---

## Converting Jython Scripts

Jython scripts are treated similarly to Python 2:
- Uses `2to3` for conversion
- Same migration preferences apply

### Jython Scripts Using `context.cursor()`

In Matillion ETL Jython, `context.cursor()` provided DB cursor access. **Python 3 does not support this.**

DPC uses **project variables** to replicate cursor functionality:
- Migration creates variables automatically
- Variables noted in migration report
- **Do not delete these variables**

#### Project Variables Created (Snowflake)

**Connection parameters:**
- `mtln_snowflake_account`
- `mtln_snowflake_username`
- `mtln_snowflake_role`
- `mtln_snowflake_warehouse`
- `mtln_snowflake_database`
- `mtln_snowflake_schema`

**Key pair authentication:**
- `mtln_snowflake_private_key_secret_name`
- `mtln_snowflake_passphrase_secret_name`
- `mtln_snowflake_passphrase_secret_key`

**Password authentication:**
- `mtln_snowflake_password_secret_name`
- `mtln_snowflake_password_secret_key`

#### Project Variables Created (Redshift)
- `mtln_redshift_host`
- `mtln_redshift_database`
- `mtln_redshift_port`
- `mtln_redshift_username`
- `mtln_redshift_password_secret_name`
- `mtln_redshift_password_secret_key`

#### Project Variables Created (Databricks)
- `mtln_databricks_host`
- `mtln_databricks_http_path` *(must be populated manually)*
- `mtln_databricks_catalog`
- `mtln_databricks_schema`
- `mtln_databricks_access_token_secret_name`
- `mtln_databricks_access_token_secret_key`
- `mtln_databricks_client_id`
- `mtln_databricks_client_secret_secret_name`
- `mtln_databricks_client_secret_secret_key`

### Jython Scripts Using Grid Variables

**Behavior difference:**
- **Matillion ETL Jython**: `context.getGridVariable()` returns a new (shallow) copy each call
- **DPC Python**: Returns reference to same underlying object

**Recommendation:** Use `copy.deepcopy()` when modifying grid variable data to avoid side effects.

---

## Converting to Python Pushdown

Python Pushdown executes Python using Snowpark in your Snowflake account.

### Steps
1. Click **Edit preferences** in **Importing files** panel
2. Toggle **Convert to Python Pushdown** to **On**
3. Configure Snowpark connection:
   - **Warehouse**: Use `[Environment Default]` or specify
   - **Python Version**: Default 3.10
   - **Script Timeout**: Default 360 seconds
4. If using Python 2/Jython, also toggle **Convert Python 2.x to 3** to On
5. Click **Apply & re-run**
6. Report shows: "Python Script component has been converted to a Python Pushdown component."
7. Click **Import**

---

## Using Automatic Variables in Python

DPC doesn't support directly accessing automatic variables in Python Script.

**Workaround:**
1. Use **Update Scalar** component to write values to user-defined variables
2. Pass those variables to the Python script

---

## Loading Additional Python Libraries

Third-party packages can't be installed with pip or apt (immutable filesystem).

**Alternative:** Supply packages via S3/Azure Blob with limitations. See DPC documentation for "Loading additional Python libraries".
