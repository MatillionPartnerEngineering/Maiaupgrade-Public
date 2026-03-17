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
