# Upgrade: Python

Reference: https://docs.matillion.com/metl/docs/migration-python/

The Data Productivity Cloud includes a **Python Script** component, but also offers other options for tasks that would require a Python Script in Matillion ETL. This includes native components such as **Print Variables**, and (for Snowflake environments) the **Python Pushdown** component.

The Python Script component works differently in the Data Productivity Cloud because there is no underlying virtual machine. The component requires a **Hybrid SaaS** deployment, and you need to bear the following in mind:

- Python scripts can't assume there is a filesystem that will persist after the script completes.
  - Unlike Matillion ETL running on a Linux VM with persistent disk, DPC agents are multiple containers and there is no guarantee a later process runs on the same container.
- DPC agents have much lower CPU and memory than Matillion ETL VMs and are not designed for compute-intensive operations.
- Only Python 3 is available.
  - If you used Python 2 or Jython interpreters, migration will warn you and scripts may need updating.
- Jython scripts can be automatically converted to Python 3 during migration, but there are differences (cursor object and grid variables).
- Python 2 scripts can be automatically converted to Python 3.
- Third party packages can't be installed with `pip` or `apt` (immutable filesystem).
  - Packages can be supplied via S3/Azure Blob with limitations (see “Loading additional Python libraries”).
- The Python version currently used by DPC is **3.10**.
  - If you are migrating a version of Python later than this, consider **Python Pushdown** instead (Snowflake only).

## Upgrade path (recommended order)

1. **Replace with native components** where possible (e.g., Print Variables). Additional examples mentioned include: Move File, Delete File, Send Email with Attachment.
2. In a **Snowflake** project, consider refactoring to use **Python Pushdown**.
   - Advantages:
     - Runs on scalable Snowflake warehouses.
     - Direct access to Snowflake database connections.
     - Designed for heavy processing (including `pandas`).
     - Full access to DPC variables.
     - Many packages accessible by default.
     - Can be secured with network access control.
   - Considerations:
     - May require Python refactoring.
     - Requires some initial Snowflake account setup.
     - Requires network access configuration.
     - Snowflake projects only.
3. Use the **Python Script** component (Hybrid SaaS only).
   - Refactor to avoid filesystem reliance.
   - Python 3 only.
4. Use **Bash Pushdown** to run Python scripts on your own Linux machine via Bash (SSH).
   - Advantages: control CPU/memory; install any packages/apps.
   - Considerations: you must manage the machine; need agent network access.

## Upgrading Python 2 scripts to Python 3

DPC supports Python 3 only. If you have Python 2 scripts, the migration tool can auto-convert them to Python 3 using `2to3`.

- `2to3` handles many common changes but you may need manual updates.
- Migration report will flag scripts requiring manual refactor and indicate upgrade is needed.

### Steps

1. Click **Edit preferences** in the **Importing files** panel.
2. Toggle **Convert Python 2.x to 3** to **On** (default Off).
3. Click **Apply & re-run**.
4. Migration report should show: “Your Python script has been auto-converted using the 2to3 tool.”
5. Click **Import** and continue.

After conversion:

- Both original and converted scripts are stored in the DPC branch:
  - `.matillion → migration → <migration date> → <pipeline name>`
- Two versions are stored: `_before` and `_after`
- These `_before`/`_after` scripts are not used by the pipeline component and can be deleted after verification.

> **Warning**  
> Matillion can't guarantee the converted script will work as expected. Always review and test thoroughly.

## Using automatic variables in a Python script

DPC doesn't support directly accessing automatic variables through the Python Script component.

- Workaround: use an **Update Scalar** component to write values to user-defined variables, then pass to the script.

## Upgrading Jython scripts

DPC supports Python 3 only. Jython scripts can be auto-converted to Python 3 during migration.

- Jython is treated similarly to Python 2.
- Uses `2to3` for conversion.
- Same migration preferences and before/after storage behavior applies.

### Jython scripts that use the cursor object

In Matillion ETL Jython, `context.cursor()` allowed access to a DB cursor. Python 3 does not support this behavior.

DPC uses **project variables** to store database connection details and replicate cursor-like functionality.

- Migration creates several project variables and notes them in the migration report (e.g., “Variable created to facilitate the use of context.cursor() within Python Script components.”)
- Do not delete these variables; they are required for converted scripts.
- Create environments prior to importing Jython scripts if possible, because variables are created based on environment configuration at import time.
  - If additional environments are created later, you may need to add variables manually.

#### Project variables created during import (by platform/warehouse)

**Cloud platform**

- Azure:
  - `mtln_azure_key_vault_uri`  
    - When using an environment with an Azure agent, if empty, the default keyvault provided in `DEFAULT_KEYVAULT` will be used.
- AWS:
  - N/A

**Data warehouse**

- Snowflake connection parameters:
  - `mtln_snowflake_account`
  - `mtln_snowflake_username`
  - `mtln_snowflake_role`
  - `mtln_snowflake_warehouse`
  - `mtln_snowflake_database`
  - `mtln_snowflake_schema`
- Snowflake key pair authentication:
  - `mtln_snowflake_private_key_secret_name`
  - `mtln_snowflake_passphrase_secret_name`
  - `mtln_snowflake_passphrase_secret_key`
- Snowflake password authentication:
  - `mtln_snowflake_password_secret_name`
  - `mtln_snowflake_password_secret_key`

- Redshift connection parameters:
  - `mtln_redshift_host`
  - `mtln_redshift_database`
  - `mtln_redshift_port`
  - `mtln_redshift_username`
- Redshift password authentication:
  - `mtln_redshift_password_secret_name`
  - `mtln_redshift_password_secret_key`

- Databricks connection parameters:
  - `mtln_databricks_host`
  - `mtln_databricks_http_path` *(must be populated manually)*
  - `mtln_databricks_catalog`
  - `mtln_databricks_schema`
- Databricks personal access token auth:
  - `mtln_databricks_access_token_secret_name`
  - `mtln_databricks_access_token_secret_key`
- Databricks OAuth auth:
  - `mtln_databricks_client_id`
  - `mtln_databricks_client_secret_secret_name`
  - `mtln_databricks_client_secret_secret_key`

### Jython scripts that use grid variables

Grid variable handling differs between Matillion ETL Jython and DPC Python:

- **Matillion ETL Jython**: `context.getGridVariable()` returns a new (shallow) copy of the list object each call; modifying the local variable does not affect subsequent retrievals.
- **DPC Python**: `context.getGridVariable()` returns a reference to the same underlying object; modifying the list affects subsequent reads in the same script.

Recommendation:

- Use `copy.deepcopy()` (or appropriate alternatives) when you intend to modify retrieved grid variable data without side effects.

## Upgrading to Python Pushdown (Snowflake)

Python Pushdown executes Python using Snowpark in your Snowflake account.

### Steps

1. Click **Edit preferences** in the **Importing files** panel.
2. Toggle **Convert to Python Pushdown** to **On** (default Off).
3. Configure the Snowpark connection properties:
   - **Warehouse**: Snowflake warehouse to execute the script (use `[Environment Default]` to use environment default).
   - **Python Version**: default currently 3.10 (available versions may change).
   - **Script Timeout**: default 360 seconds (cannot exceed Snowflake internal query timeout limits).
4. Selected values apply to **all** Python Pushdown components; other properties must be configured per component.
5. If using Python 2/Jython, scripts must be converted to Python 3 (toggle **Convert Python 2.x to 3** to On).
6. Click **Apply & re-run**.
7. Migration report should show: “Python Script component has been converted to a Python Pushdown component.”
8. Click **Import** and continue.
