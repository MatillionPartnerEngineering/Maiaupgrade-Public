---
name: migration-variables
description: Use when refactoring variables, automatic variables, export variables, or system variables during Matillion ETL to DPC migration.
---

# Variables Migration Guide

Reference: https://docs.matillion.com/metl/docs/migration-variables/

## Variable Type Mapping

| Matillion ETL | DPC Equivalent |
|---------------|----------------|
| Environment variables | **Project variables** |
| Job variables | **Pipeline variables** |
| Grid variables | **Pipeline variable** (type: grid) |

## Key Differences

- Date formats not supported → All `DATETIME` converted to `STRING`
- `STRUCT` formats not supported
- Scalar and grid variables **cannot share the same name** (grid is now a pipeline variable type)

---

## Automatic Variables → System Variables

Reference: https://docs.matillion.com/metl/docs/migration-automatic-variables/

### Syntax Change

| Platform | Syntax |
|----------|--------|
| Matillion ETL | `${my_variable_name}` |
| DPC | `${sysvar.object.property}` |

### Variable Mappings

| Matillion ETL | DPC System Variable |
|---------------|---------------------|
| `component_name` | `thisComponent.name` |
| `component_message` | `thisComponent.message` |
| `environment_name` | `environment.name` |
| `job_name` | `thisPipeline.fullName` |
| `project_id` | `project.id` |
| `run_history_id` | `rootPipeline.executionId` |
| `task_id` | `thisComponent.taskId` |
| `version_name` | `artifact.versionName` |

> **Note:** In DPC, these are **UUIDs** (not integers):
> - `project.id`
> - `rootPipeline.executionID`
> - `thisComponent.taskID`
>
> Store as `TEXT` rather than `INTEGER`.

### Not Yet Supported (Planned)

- `environment_username`
- `environment_database`
- `environment_default_schema`
- `project_name`
- `queued_time`

### Not Supported (Architecture Differences)

- `detailed_error`
- `component_id`
- `job_id` (use `artifact.versionName` + `thisPipeline.fullName` instead)
- `project_group_id`
- `project_group_name`
- `version_id`
- `environment_catalog`
- `environment_endpoint`
- `environment_id`
- `environment_port`

### Accessing Variables in Scripts

DPC doesn't support directly accessing automatic variables in Python/Bash scripts.

**Workaround:**
1. Use **Update Scalar** to write values to user-defined variables
2. Pass those variables to scripts

---

## Export Variables → System Variables

Reference: https://docs.matillion.com/metl/docs/migration-export-variables/

### Common Export Variable Mappings

| Matillion ETL Export | DPC System Variable |
|---------------------|---------------------|
| Completed At | `thisComponent.finishedAt` |
| Component | `thisComponent.name` |
| Duration | `thisComponent.duration` |
| Message | `thisComponent.message` |
| Row Count | `thisComponent.rowCount` |
| Started At | `thisComponent.startedAt` |
| Status | `thisComponent.status` |

### Component-Specific Exports (Supported)

| Component | Export Variable | DPC System Variable |
|-----------|-----------------|---------------------|
| SQL Query | Query ID | `thisComponent.queryId` |
| Table update | Rows Deleted | `thisComponent.rowsDeleted` |
| Table update | Rows Inserted | `thisComponent.rowsInserted` |
| Table update | Rows Updated | `thisComponent.rowsUpdated` |

### Export Variables Without DPC Equivalents

These require refactoring:

| Component | Missing Export |
|-----------|---------------|
| Append to Grid | Rows Added |
| Create Stream | Stream Recreated |
| Create Table | Table Recreated |
| Data Transfer | Bytes Written |
| Extract components | Data Structure |
| Iterator components | Iterations Attempted, Generated, Successful |
| JDBC Table Metadata to Grid | Column Count |
| Query components | Filename, Time Taken to Load/Stage |
| Remove from Grid | Rows Removed |
| Retry | Iterations Attempted, Generated, Successful |

### Not Supported in DPC

- Returning grid variables from child pipelines
- Component-specific properties (e.g., "Iterations generated")
- System variables in **If** component (use **Advanced** mode)
- User defined variables

---

## Remove from Grid Changes

The component is improved in DPC — **Fixed/Grid** option no longer needed.

**If Fixed/Grid = Grid in Matillion ETL:**
- Selected grid mappings are lost on migration
- To restore: Set **Values Grid** to **Use Grid Variable** and select mappings again

**If Fixed/Grid = Fixed:**
- Component works without mitigation

---

## Variables in Iterators

Currently it isn't possible to control iterator concurrency using a variable.
- Edit the component and set **Concurrency** manually

---

## Environment Variable Defaults

To migrate default values:

1. Export from Matillion ETL **must include** environments whose defaults you want
2. DPC project must have environments matching each exported environment:
   - If exporting `envName`, DPC env must be `envName` or have suffix `-envName`
3. Variables must be of a type supported by DPC

> **Note:** Descriptions limited to **255 characters** (longer will be truncated).
> Default value imports as **Environment default override**, not **Default value**.
