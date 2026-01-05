# Matillion ETL → Data Productivity Cloud (DPC): Migration Feature Differences & Upgrade Notes

> Source text provided by user (copied from Matillion migration documentation).  
> Intended use: baseline spec to derive unit tests across imported pipelines in DPC.

---

## Feature differences in the Data Productivity Cloud

Some components and features need specific treatment, mitigation, or workarounds when migrated. If you use any of the following features, make sure you understand what specific treatment each one will require.

---

## API trigger

API triggers are supported in the Data Productivity Cloud, but the API works differently. Read the API documentation for further details.

- You may need to update your trigger scripts to work with the Data Productivity Cloud API.
- Evaluate your triggers on a case-by-case basis and update where needed, guided by the API documentation.

---

## Git

Unlike Matillion ETL where Git integration is an optional feature, the Data Productivity Cloud is built with Git as an integral element, providing pipeline version control and making it simple to collaborate and manage data pipelines within your team. Read **Git in Designer** to learn more about this feature of the Data Productivity Cloud.

If you currently use Git in Matillion ETL, it’s not recommended that you use the same Git repository for the Data Productivity Cloud:

- The Data Productivity Cloud won’t recognize the format of Matillion ETL files stored in Git.
- Although it is possible to connect to the same repository, you won’t be able to access your previous Git history.

### Recommended migration process for Git users

1. Create a Data Productivity Cloud project using the **Connect your own Git repository** option.
2. Connect the project to a **new** Git repository with your preferred provider.
3. Migrate jobs that use Git.
4. Perform any necessary manual changes to the imported pipelines.
5. Commit and push the migrated pipelines to the Data Productivity Cloud Git repository.

### If you don’t currently use Git in Matillion ETL

- Select which type of Git repository you want to use in the Data Productivity Cloud and configure it prior to migrating your jobs.

---

## OAuths

For security reasons, credentials such as OAuths are **not migrated** from Matillion ETL to the Data Productivity Cloud.

- Any OAuths you have set up in Matillion ETL must be recreated manually in the Data Productivity Cloud to allow pipelines to run.
- Read **OAuth** for details.

---

## Secrets

For security reasons, credentials such as secrets and passwords are **not migrated** from Matillion ETL to the Data Productivity Cloud.

- Any secrets or other credentials you have set up in Matillion ETL must be recreated manually in the Data Productivity Cloud to allow pipelines to run.
- Read **Secrets and secret definitions** and **Cloud provider credentials** for details.

Passwords can’t be entered directly into Data Productivity Cloud components (by design). All passwords must be stored in **secrets**, which the component references.

- Secrets are stored in:
  - DPC secret manager in a **Full SaaS** environment, or
  - your own cloud platform’s secret manager in a **Hybrid SaaS** environment.

### Steps

1. Create secrets with the credentials that your pipelines will need to connect to third-party services.
2. Update components to point to the secrets you have created.

---

## Webhook and queue triggers for pipelines

The Data Productivity Cloud doesn’t natively support triggering pipelines from a webhook or a queue such as SQS or Azure Queue.

- DPC architecture should avoid some internal queuing/scaling/availability limitations that can make a queue necessary for Matillion ETL, making webhook/queue triggers unnecessary in most scenarios.
- Recommended approach: use the DPC **API** for running pipelines directly.

If you need to integrate DPC with existing webhook/queue systems (e.g., trigger a pipeline when a file lands in S3):

- Use **AWS Lambda** or **Azure Functions** to implement an API call based on an event.

---

# Upgrade: API Extract

Reference: https://docs.matillion.com/metl/docs/migration-api-extract/

The Data Productivity Cloud replaces Matillion ETL’s **API Extract** component with **custom connectors**, which can be configured to connect to any compatible third-party API.

- Migrated pipelines will use a custom connector that replicates API Extract functionality.
- Most configuration from your API Extract profile is preserved, but some settings require manual reconfiguration.

> **Note**  
> If your job uses the **API Query** component, read **API Query** instead.

## Upgrade path

1. Export existing API Extract profiles from Matillion ETL and import them into DPC.  
   This creates an equivalent custom connector, preserving much of the configuration.
2. Export the Matillion ETL job that uses API Extract and import it into DPC.  
   The new pipeline will reference the custom connector created from the imported profile.

## Exporting and importing extract profiles

In Matillion ETL:

1. Click **Project → Manage API Profiles → Manage Extract Profiles**.
2. In **Manage Extract Profiles**, locate the profile and click the download icon.  
   This downloads a `.json` file to your local filesystem.

In Data Productivity Cloud:

3. Navigate to DPC.
4. In the left navigation, click the **Custom Connectors** icon, then select **Custom Connectors**.
5. In the top-right, click **Import**.
6. In **Import connector**, select the exported `.json` file and click **Import**.

After import:

7. Review the imported configuration to ensure endpoints/authentication/parameters are correct.
8. Keep the **same name** as the API Extract profile so the pipeline references it correctly.
9. **Pagination isn’t imported** and must be configured from scratch in DPC (strategies follow the same concepts).
   - DPC offers **script pagination**; if all endpoints share the same pagination logic, you can reuse a single script.
10. Create a new **authentication configuration** in DPC and assign it to each endpoint manually.
    - Authentication type is inferred from the imported profile.
11. Parameters are inferred and typically require no manual reconfiguration.
    - Headers are preserved.
    - Request body (if configured) is retained.
12. Click **Save** (required even if you made no manual changes).

## Configuring the custom connector in the pipeline

1. Export the Matillion ETL job containing API Extract and import it into DPC.
2. The imported pipeline replaces API Extract with a **Custom Connector** component.
3. Manual work required:
   - Configure authentication (secrets aren’t imported).
   - Review default values for properties that didn’t exist in Matillion ETL.
   - Update service-specific parameters if the DPC environment differs (e.g., S3 → Azure Blob).
   - Validate output schema differences and adjust downstream components.

## Platform-specific information

### Snowflake and Amazon Redshift

- If **Load Selected Data = No** and a repeat element is configured:
  - Raw JSON is staged into:
    - Snowflake: `VARIANT` column named **Data Value**
    - Redshift: `SUPER` column named **data**
- If no repeat element:
  - System loads data according to schema definition and automatically unnests first nesting level (may appear flattened).
- To ensure compatibility in Matillion ETL so migrated transformation pipelines can use the data as-is:
  - Set **Load Selected Data = No**

### Databricks

- Data is always loaded according to the defined schema.
- No implicit flattening/nesting manipulation.

## Best practices

- Start with non-authenticated or non-paginated API Extract pipelines (import cleanly).
- Use custom connector preview to validate config before creating pipelines.
- Review schema settings and adjust data type mappings if discrepancies occur.

## Comparing API Extract and custom connectors

| Feature | API Extract | Custom Connector | Notes |
|---|---|---|---|
| Profiles | Configured in Matillion ETL | Imported or created in custom connector |  |
| Pagination | Configured per endpoint | Configured per endpoint; supports script pagination | Not imported; must be configured again |
| Headers/Parameters | Manually defined | Manually defined or inferred from imported profile |  |
| Authentication | Configured in API Extract component | Defined once and assigned to each endpoint | Not imported; must be configured again |
| Flattening/Schema | Basic JSON flattening | Depends on repeat element config in Matillion ETL |  |
| Load Selected Data | Implicit from schema | Must be configured in DPC | Set to `FALSE` to match ETL behavior or `TRUE` as a refactor |
| Semi-structured handling | Component-specific | Warehouse-specific |  |

---

# Upgrade: API Query

Reference: https://docs.matillion.com/metl/docs/migration-api-query/

> **Note**  
> DPC API Query solution is only available if you’re using agent version **10.1232.0+**. Read **Agent version tracks**.

When migrating a job that includes an **API Query** component:

- The API Query component migrates automatically.
- The **API Query Profile** used by the component is **not** automatically migrated.
- In the migrated pipeline, the API Query component is present but fails validation.
- Upgrade report shows the configuration file (query profile) is missing.

> **Note**  
> If your job uses **API Extract**, read **API Extract** instead.

## Upgrade path

Export the API Query profile from Matillion ETL and import it into DPC.

### Steps

In Matillion ETL:

1. Click **Project → Manage API Profiles → Manage Query Profiles**.
2. Locate the profile and click download icon to export a `.json`.

> **Note**  
> If multiple profiles must be downloaded, consider using the Matillion ETL API to download multiple profiles to one `.json`.

In Data Productivity Cloud:

3. Open your DPC project and branch.
4. In the **Files** panel:
   - Click `...` next to the folder you want to import to, **or**
   - Click **Add** → **Import**
5. Select the exported `.json` file and click **Open**.

> **Note**  
> The file can contain multiple profiles; all will be imported.

6. In **Importing files**, click the **API query profiles** tab and verify expected profiles.
7. After import, profiles appear as `<profile>.rsd` under:
   - `.matillion/api-query-profiles/<component name>/<profile>.rsd`
8. API Query component should now validate.

---

# Upgrade: Bash scripts

Reference: https://docs.matillion.com/metl/docs/migration-bash/

Any **Bash Script** component will automatically import as a Bash Script component that utilizes the native computing resources of DPC to run. This may require refactor. If you want to use another server’s resources to execute the script, use the migration path below.

Unlike Matillion ETL, which runs on your own Linux VM, DPC uses a SaaS model (no underlying VM). Use **Bash Pushdown** to run Bash scripts on a Linux VM you provide and connect to via SSH.

## Advantages of Bash Pushdown

- You can set CPU and memory on the Linux VM as needed.
- You can install packages/third-party applications on the Linux VM.

## Considerations for Bash Pushdown

- You must set up, secure, update, and manage the Linux VM yourself.
- You need network access from the DPC agent to the VM.

## Upgrade path (convert to Bash Pushdown)

1. Click **Edit preferences** in the **Importing files** panel.
2. Toggle **Convert to Bash Pushdown** to **On** (default is Off).
3. Configure connection parameters:
   - **Host**: hostname or IP
   - **User Name**
   - **Connection Timeout (ms)**: default 3000
   - **Port**: default 22
   - **Authentication Type**: Password or Key Pair
     - Password: select a secret containing password
     - Key Pair: select a secret containing private key
       - If passphrase protected: set **Require Passphrase = Yes**, select passphrase secret

> **Note**  
> Read **Secrets and secret definitions** to learn how to create a new secret definition.  
> See **Bash Pushdown** documentation for other properties.

4. Click **Apply & re-run**.
5. Migration report should show: “Bash Script component has been converted to a Bash Pushdown component.”
6. Click **Import** and continue.

## Alternative approaches

If you choose not to use Bash Pushdown:

- See if functionality has a native component equivalent (e.g., **Print Variables**).
- See if workload can be written in **Python Pushdown** (Snowflake only).
- See if workload can be written in **Python Script** (Hybrid SaaS only).
- You can continue to use Bash Script without converting, but this is not recommended:
  - It won’t run in **Full SaaS**
  - It may run with problems in **Hybrid SaaS**
  - Discuss with Matillion Support if needed

## Automatic variables (Bash)

DPC doesn’t support directly accessing automatic variables through the **Bash Script** component.

- Workaround: use **Update Scalar** to write values to user-defined variables, then pass to script.

---

# Upgrade: Automatic variables

Reference: https://docs.matillion.com/metl/docs/migration-automatic-variables/

DPC supports most automatic variables and includes a similar concept called **System variables**. They differ in syntax:

- Matillion ETL: `${my_variable_name}`
- DPC: `${sysvar.object.property}`

A migration pathway exists for mapping these variables, but you must manually edit pipeline components to use the correct variables.

For more details, read **Upgrade: Variables** and **List of system variables**.

## Upgrade path: mappings

| Matillion ETL automatic variable | DPC system variable |
|---|---|
| `component_name` | `thisComponent.name` |
| `component_message` | `thisComponent.message` |
| `environment_name` | `environment.name` |
| `job_name` | `thisPipeline.fullName` |
| `project_id` | `project.id` |
| `run_history_id` | `rootPipeline.executionId` |
| `task_id` | `thisComponent.taskId` |
| `version_name` | `artifact.versionName` |

> **Note**  
> In DPC, the following are UUIDs rather than integers:  
> - `.project.id`  
> - `.rootPipeline.executionID`  
> - `.thisComponent.taskID`  
> You may need to store as `TEXT` rather than `INTEGER`.

## Not yet supported

No equivalents currently (support planned in a future release; see Roadmap):

- Environment properties:
  - `environment_username`
  - `environment_database`
  - `environment_default_schema`
- `project_name`
- `queued_time`

## Not supported

No equivalents due to architecture differences:

- `detailed_error`
- `component_id`
- `job_id` (see below)
- `project_group_id`
- `project_group_name`
- `version_id`
- `environment_catalog`
- `environment_endpoint`
- `environment_id`
- `environment_port`

## Accessing through scripts

DPC doesn’t support directly accessing automatic variables through **Python Script** or **Bash Script**.

- Workaround: use **Update Scalar** to write values to user-defined variables and pass to scripts.
- For alternatives, read **Upgrade: Bash** and **Upgrade: Python**.

## `job_id`

In Matillion ETL, `job_id` uniquely identifies jobs even if renamed.

In DPC, track jobs using:

- `${sysvar.artifact.versionName}` (artifact version)
- `${sysvar.thisPipeline.fullName}` (pipeline name)

Together these provide a unique identifier per job execution similar to `job_id`.

---

# Upgrade: Database Query

Reference: https://docs.matillion.com/metl/docs/migration-database-query/

DPC has a **Database Query** component equivalent to Matillion ETL’s Database Query component.

- Vendor restrictions prevent shipping drivers for every database.
- DPC supports uploading additional drivers via a mechanism.

## Upgrade path

The source database determines the upgrade path.

### Upgraded automatically

Database Query components with the following sources migrate automatically:

- Amazon Redshift
- IBM DB2 for i
- MariaDB
- Microsoft SQL Server
- Oracle
- PostgreSQL
- Sybase ASE
- Snowflake
- SQL Server (Microsoft driver)

### Upgrade with a driver upload (Hybrid SaaS only)

If not supported by default:

- The component is automatically changed to **JDBC** and properties configured where possible.
- You must upload a suitable JDBC driver for each source.
- You must create a **manifest file** per JDBC component documentation.

> **Note**  
> This option is available for **Hybrid SaaS deployments only**.

### MySQL

- DPC can’t ship/use the official MySQL driver.
- Uses MariaDB driver (compatible).
- MySQL Database Query components are changed to refer to MariaDB driver during migration.
- If you need the official MySQL driver:
  - Use JDBC and provide your own driver.

---

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

# Upgrade: Export variables

Reference: https://docs.matillion.com/metl/docs/migration-export-variables/

Matillion ETL **export variables** are called **system variables** in the Data Productivity Cloud (DPC), and operate in broadly the same way, with a few notable differences. For more details of variable migration in general, read **Upgrade: Variables**.

## Upgrade path

- Mappings of component exports to job or environment variables are automatically migrated to the Data Productivity Cloud. For more information, read **Upgrade: Variables**.
- The following table lists the Data Productivity Cloud equivalents for some commonly used export variables. This list isn't exhaustive—consult the Data Productivity Cloud documentation for an up-to-date list of **system variables**.

### Common export variable equivalents

| Matillion ETL component export | Data Productivity Cloud system variable |
|---|---|
| Completed At | `thisComponent.finishedAt` |
| Component | `thisComponent.name` |
| Duration | `thisComponent.duration` |
| Message | `thisComponent.message` |
| Row Count | `thisComponent.rowCount` |
| Started At | `thisComponent.startedAt` |
| Status | `thisComponent.status` |

### Component-specific export variables that can be migrated

| Matillion ETL component | Matillion ETL export variable | Data Productivity Cloud system variable |
|---|---|---|
| SQL Query | Query ID | `thisComponent.queryId` |
| Table update | Rows Deleted | `thisComponent.rowsDeleted` |
| Table update | Rows Inserted | `thisComponent.rowsInserted` |
| Table update | Rows Updated | `thisComponent.rowsUpdated` |

### Component export variables with no equivalents (non-exhaustive examples)

Some Matillion ETL components have export variables that currently have **no** equivalents in the Data Productivity Cloud, and you will have to refactor to work around these. Common examples include:

- **Append to Grid**: Rows Added
- **Create Stream**: Stream Recreated
- **Create Table**: Table Recreated
- **Data Transfer**: Bytes Written
- **Extract components** (e.g., API Extract, Amplitude Extract, etc.): Data Structure
- **Iterator components**: Iterations Attempted, Iterations Generated, Iterations Successful
- **JDBC Table Metadata to Grid**: Column Count
- **Query components** (e.g., Database Query, DynamoDB Query, Email Query, etc.): Filename, Time Taken to Load, Time Taken to Stage
- **Remove from Grid**: Rows Removed
- **Retry**: Iterations Attempted, Iterations Generated, Iterations Successful

## Functionality not supported

The following are not currently supported in the Data Productivity Cloud. If your Matillion ETL jobs incorporate any of these, you will need to refactor the migrated pipelines:

- Returning grid variables from a child pipeline.
- Component-specific properties (for example, "Iterations generated").
- Use of system variables in an **If** component. This can only be done in the Data Productivity Cloud using **Advanced** mode.
- User defined variables.

---

# Upgrade: Extract Nested Data

Reference: https://docs.matillion.com/metl/docs/migration-extract-nested-data/

In Matillion ETL for Databricks, the **Extract Nested Data** component uses the **Struct** data type to flatten nested data.

In the Data Productivity Cloud, the **Extract Nested Data** component for Databricks instead uses the **Variant** data type. This results in different behavior compared to Matillion ETL.

To preserve the original behavior for Databricks projects, the Data Productivity Cloud provides a separate component—**Extract Structured Data**—which continues to use the **Struct** data type.

## Upgrade mapping

During migration of Databricks projects from Matillion ETL to the Data Productivity Cloud:

- The **Extract Nested Data** component from Matillion ETL will be mapped to the **Extract Structured Data** component in the Data Productivity Cloud.
- This ensures equivalent functionality and preserves pipeline behavior.

> **Note**  
> While the Data Productivity Cloud includes an Extract Nested Data component for Databricks, it isn't used during migration due to its reliance on the **Variant** type.

The mapping applies **only** to Databricks projects. Snowflake and Amazon Redshift projects are unaffected and don't require any special component mapping.

---

# Upgrade: Filter

Reference: https://docs.matillion.com/metl/docs/upgrade-filter/

The Data Productivity Cloud has a **Filter** component that's equivalent to the Matillion ETL **Filter** component, so Filter components will migrate automatically.

The Filter components for **Databricks** in Matillion ETL and the Data Productivity Cloud have some functionality differences in how single quotes (`'`), double quotes (`"`), and backticks (`` ` ``) are handled in filter expressions. Manual intervention may be required after migration to ensure the filter expressions behave as expected.

## Upgrade path for Databricks

When migrating Matillion ETL Filter components that target Databricks, the quoting behavior of filter expressions may differ between Matillion ETL and the Data Productivity Cloud. This is due to differences in how the two platforms handle quotes in SQL expressions.

A referenced table (and an attached image) summarizes how different uses of quotes in Matillion ETL Filter components will be handled during migration to the Data Productivity Cloud. If you have filter expressions that use quotes, you should review them after migration to ensure they behave as expected.

SQL Data Productivity Cloud imported is the resulting quoting of the SQL in the Data Productivity Cloud.

| Filter value | Source column type | SQL Matillion ETL | SQL Data Productivity Cloud | Value on import | SQL Data Productivity Cloud imported |
|---|---|---|---|---|---|
| `a` | string/text | `'a'` | `'a'` | `a` | `'a'` |
| `'a'` | string/text | `'a'` | `'\''a'\''` | `a` | `'a'` |
| `"a"` | string/text | `` `a` `` | `"a"` | `` `a` `` | `` `a` `` |
| `` `a` `` | string/text | `` `a` `` | `` `a` `` | `` `a` `` | `` `a` `` |
| `2025-11-24` | datetime-like/boolean | `'2025-11-24'` | `'2025-11-24'` | `2025-11-24` | `'2025-11-24'` |
| `'2025-11-24'` | datetime-like/boolean | `'2025-11-24'` | `'2025-11-24'` | `2025-11-24` | `'2025-11-24'` |
| `"a"` | datetime-like/boolean | `` `a` `` | `"a"` | `` `a` `` | `` `a` `` |
| `` `a` `` | datetime-like/boolean | `` `a` `` | `` `a` `` | `` `a` `` | `` `a` `` |
| `1` | anything else | `'1'` | `1` | `1` | `1` |
| `'1'` | anything else | `'1'` | `'1'` | `1` | `1` |
| `"a"` | anything else | `` `a` `` | `"a"` | `` `a` `` | `` `a` `` |
| `` `a` `` | anything else | `` `a` `` | `` `a` `` | `` `a` `` | `` `a` `` |


---

# Upgrade: Iterators

Reference: https://docs.matillion.com/metl/docs/migration-iterators/

All Matillion ETL iterator components will be migrated to the Data Productivity Cloud. However, the **Stop On Condition** property does not exist in the Data Productivity Cloud.

## Upgrade path

- Iterators with **Stop on Condition = No** in Matillion ETL will migrate to the Data Productivity Cloud without any issues, and will perform as expected.
- Iterators with **Stop on Condition = Yes** in Matillion ETL will migrate to the Data Productivity Cloud, but pipelines may not perform as expected due to this property being missing. You should refactor your pipelines, if possible, to work without requiring this property.

---

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

---

# Upgrade: Replicate

Reference: https://docs.matillion.com/metl/docs/migration-replicate/

The **Replicate** component isn't needed in the Data Productivity Cloud, as all components have multiple outputs by default.

## Upgrade path

- During migration, Replicate components are automatically removed from the pipeline.
- Connections previously routed through Replicate are established directly.
- No manual intervention is required.

---

# Upgrade: Temporary tables

Reference: https://docs.matillion.com/metl/docs/migration-temporary-tables/

Due to the distributed nature of the Data Productivity Cloud, temporary tables can't be supported.

- Temporary tables exist only within the database session that created them.
- DPC creates multiple sessions for parallelism, making it impossible to reference temporary tables.

## Upgrade path

Refactor migrated pipelines to use:

- **Transient tables** in Snowflake
- **Permanent tables** in Databricks
- **Permanent tables** in Amazon Redshift

---

# Upgrade: Text Output

Reference: https://docs.matillion.com/metl/docs/migration-text-output/

The **Text Output** component for Amazon Redshift in Matillion ETL is mapped to the **S3 Unload** component in the Data Productivity Cloud.

## Upgrade path

Text Output components in Amazon Redshift jobs are automatically replaced by S3 Unload during migration. Properties are mapped as follows:

| Text Output property | S3 Unload property | Notes |
|---|---|---|
| Schema | Schema | No change. |
| Table Name | Table Name | No change. |
| S3 URL Location | S3 URL Location | No change. |
| S3 Object Prefix | S3 Object Prefix | No change. |
| Delimiter | Delimiter | If delimiter isn’t a comma, S3 Unload sets Data File Type = Delimited and copies delimiter. |
| Compress Data | Compress Data | No change. |
| Null As | NULL As | No change. |
| Output Type | Data File Type | If Output Type = Escaped, Escape = Yes. |
| Multiple Files | Parallel | Filename behavior differs; S3 Unload always appends file number to prefix. |
| Row limit per file | *(not migrated)* | S3 Unload limits by file size via Max File Size. |
| Include Header | Include Header | No change. |
| Null Handling | *(not migrated)* | Null handling isn’t supported in S3 Unload. |
| Encryption | Encryption | No change. |
| KMS Key ID | KMS Key Id | No change. |

When there are parameter differences, the migration tool will issue a warning advising you to refer to documentation, and you may need to manually reconfigure S3 Unload properties.

> **Note**  
> In S3 Unload, selecting **Fixed Width** hides **Escape** and **Add quotes**. If Fixed Width is selected while both Escape and Add quotes are Yes, migration is blocked.

---

# Upgrade: Transactions

Reference: https://docs.matillion.com/metl/docs/migration-transactions/

The Data Productivity Cloud supports **Begin**, **Commit**, and **Rollback** transaction components, similar to Matillion ETL.

Key difference:

- In Matillion ETL, any component could run inside a transaction.
- In DPC, only these run inside a transaction:
  - **Run Transform**
  - **SQL Script** *(use with caution; DDL forces commit)*

Other components (including ingestion components) will run outside the transaction without a runtime error.

## Upgrade path

Transactions migrate automatically without intervention. If jobs relied on forced commits within the transaction (e.g., DDL behavior), refactor since this behavior is no longer permitted.

---

# Upgrade: Variables

Reference: https://docs.matillion.com/metl/docs/migration-variables/

Matillion ETL job variables, environment variables, and grid variables will be migrated:

- Environment variables → **project variables**
- Job variables → **pipeline variables**
- Grid variables → a type of **pipeline variable**

Read **Variables** and **Grid variables** for details.

## Upgrade path

Most variables migrate automatically, but key differences:

- Date formats for variables aren’t supported; migration tool converts all `DATETIME` variables to `STRING`.
- `STRUCT` formats for variables aren’t supported.
- Scalar and grid pipeline variables can’t share the same name (grid is now a pipeline variable type).

If any of these apply, refactor accordingly.

## Remove from Grid

The **Remove from Grid** component is improved in DPC so **Fixed/Grid** is no longer needed.

- If Matillion ETL Remove from Grid had Fixed/Grid = Grid:
  - Selected grid mappings are lost on migration.
  - To restore: set **Values Grid** to **Use Grid Variable** and select mappings again.
- If Fixed/Grid = Fixed:
  - Migrated component continues to work without mitigation.

## Automatic variables

Read **Upgrade: Automatic variables** for full details of differences.

## Export variables

Matillion ETL export variables are called **system variables** in DPC. For details, read **Upgrade: Export variables**.

## Variables in iterator components

Currently it isn't possible to control iterator concurrency using a variable. If your job did this, edit the component and set **Concurrency** manually.

## Environment variables default values

Default values can be migrated, with considerations:

- When exporting from Matillion ETL, export **must** include the environments whose defaults you want to keep.
  - This migrates only variable defaults, not other environment settings.
- The DPC project must have environments matching each exported Matillion ETL environment:
  - If exporting `envName`, DPC env must be `envName` or have suffix `-envName` (e.g., `projectName-envName`).
- Variables must be of a type supported by DPC.

> **Note**  
> Environment variable descriptions are limited to **255 characters** during migration; longer descriptions will be truncated.  
> The default value is imported as the **Environment default override** for each named environment, **not** as the **Default value**.
