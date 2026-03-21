# Matillion ETL → Data Productivity Cloud  
## Governed Migration Framework (Maia-Managed)

This repository contains a **governed, auditable framework** for migrating customers from **Matillion ETL** to **Matillion Data Productivity Cloud (DPC)**.

The framework is designed to be operated by **Maia**, Matillion’s Migration Project Manager LLM, and enforces strict separation between:

- Discovery  
- Refactor  
- Validation  
- Execution  

This approach enables **large-scale, multi-workload migrations** with clear governance, human oversight, and deterministic outcomes.

---

# 🧠 Primary Entry Point

### `.matillion/maia/rules/migration_manager_instructions.md`

This file is the **operational brain** of the migration system.

It defines:

- Maia’s role and authority  
- Migration phase sequencing  
- Required project structure  
- Governance and approval gates  
- Validation and execution rules  
- How migration artifacts are generated and maintained  

If you read **one file**, read this one.

---

# 📁 Repository Structure

```plaintext
.matillion/
└── maia/
    ├── rules/
    │   └── migration_manager_instructions.md
    │
    └── skills/
        ├── migration-validation/
        │   └── SKILL.md
        ├── migration-python/
        │   └── SKILL.md
        ├── migration-api-upgrade/
        │   └── SKILL.md
        ├── migration-bash/
        │   └── SKILL.md
        ├── migration-connectors/
        │   └── SKILL.md
        ├── migration-database-query/
        │   └── SKILL.md
        ├── migration-oracle/
        │   └── SKILL.md
        ├── migration-dbt/
        │   └── SKILL.md
        ├── migration-databricks/
        │   └── SKILL.md
        ├── migration-variables/
        │   └── SKILL.md
        ├── migration-automatic-variables/
        │   └── SKILL.md
        ├── migration-shared-jobs/
        │   └── SKILL.md
        ├── migration-secret-references/
        │   └── SKILL.md
        ├── migration-documentation/
        │   └── SKILL.md
        ├── migration-create-table-partial-grid-variable/
        │   └── SKILL.md
        ├── migration-strategy-and-plan-template/
        │   └── SKILL.md
        ├── migration-weekly-update/
        │   └── SKILL.md
        ├── migration-blocker-triage/
        │   └── SKILL.md
        ├── migration-test-execution/
        │   └── SKILL.md
        ├── migration-customer-actions/
        │   └── SKILL.md
        ├── migration-credentials-audit/
        │   └── SKILL.md
        ├── migration-environment-hardcoding/
        │   └── SKILL.md
        ├── migration-infrastructure-prerequisites/
        │   └── SKILL.md
        ├── migration-salesforce-query-load/
        │   └── SKILL.md
        ├── migration-netsuite/
        │   └── SKILL.md
        ├── migration-postgresql/
        │   └── SKILL.md
        ├── migration-dpc-performance/
        │   └── SKILL.md
        ├── migration-dpc-component-behaviour/
        │   └── SKILL.md
        ├── migration-unknown-component-conversion/
        │   └── SKILL.md
        ├── migration-hardcoded-credential-detection/
        │   └── SKILL.md
        ├── migration-sns-authentication/
        │   └── SKILL.md
        ├── migration-rds-query-validation/
        │   └── SKILL.md
        └── migration-s3-iam-credential-setup/
            └── SKILL.md

migration_project/
├── customer_migration_workspace/
│   ├── pipeline_component_inventory.md
│   ├── MAUD.md
│   ├── shared_jobs.md
│   └── refactor_components.md
│
└── validation_reports/
```

# 🧩 Core System Concepts

## Maia Rules

Located in:


.matillion/maia/rules/


Rules define the **governance layer** of the migration framework, including:

- Migration phases
- Approval gates
- Project state management
- Required artifacts
- Execution authority

The rules ensure migrations remain **deterministic, auditable, and controlled**.

---

## Maia Skills

Located in:


.matillion/maia/skills/


Skills provide **targeted technical expertise** used by Maia during migration.

Each skill activates automatically when relevant migration conditions are detected.

### Examples

| Skill | Purpose |
|------|------|
| `migration-validation` | Detect refactor conditions and generate validation reports |
| `migration-python` | Convert Python 2 / Jython components, Python Pushdown |
| `migration-api-upgrade` | Migrate API Extract and API Query components |
| `migration-bash` | Convert Bash scripts to Bash Pushdown |
| `migration-connectors` | Resolve JDBC and database connector issues |
| `migration-database-query` | Database Query upgrade paths and driver compatibility |
| `migration-oracle` | Oracle-specific performance, fetch size, data integrity, and authentication patterns |
| `migration-dbt` | dbt Core repository config and Sync File Source removal |
| `migration-databricks` | Handle Databricks-specific migration differences |
| `migration-variables` | Map variable types (env, job, grid) to DPC equivalents |
| `migration-automatic-variables` | Map automatic variables to DPC system variable syntax |
| `migration-shared-jobs` | Unpack, export, import, and refactor shared jobs |
| `migration-secret-references` | Fix incorrectly formatted secret references and missing concurrencyMethod |
| `migration-documentation` | Master feature differences and migration specs |
| `migration-create-table-partial-grid-variable` | Expand partial grid variables to full Create Table schema |
| `migration-strategy-and-plan-template` | Customer migration strategy with progress tracking |
| `migration-weekly-update` | Weekly migration status update template |
| `migration-blocker-triage` | Escalation decision tree and blocker categorization for failures |
| `migration-test-execution` | Phased test execution methodology for migrated workloads |
| `migration-customer-actions` | Template for creating and tracking customer action items |
| `migration-credentials-audit` | Pre-execution audit of hardcoded credentials and secret references |
| `migration-environment-hardcoding` | Detect and remediate hardcoded environment references in pipelines |
| `migration-infrastructure-prerequisites` | Pre-execution checklist for infrastructure dependencies |
| `migration-salesforce-query-load` | Salesforce Query/Load gotchas, OAuth patterns, API selection, and migration guidance |
| `migration-netsuite` | NetSuite connector gotchas, auth patterns, driver management, and performance tuning |
| `migration-postgresql` | PostgreSQL connector gotchas, JSONB handling, case-sensitivity, driver changes, and METL internal DB upgrades |
| `migration-dpc-performance` | DPC architecture dispatch tax, component overhead, CIS limits, and optimisation strategies |
| `migration-dpc-component-behaviour` | Component behaviour drift (iterators, Join, CALC), agent stability, Git, SQS gaps, and known limitations |
| `migration-unknown-component-conversion` | Detect and convert unknown-orchestration components back to proper DPC types (Excel Query mapping included) |
| `migration-hardcoded-credential-detection` | Detect and remediate hardcoded passwords, usernames, and connection strings in migrated pipelines |
| `migration-sns-authentication` | SNS Message component AWS auth setup, IAM permissions, and triage priority |
| `migration-rds-query-validation` | RDS Query structural validation errors, skipped component issues, and credential conversion |
| `migration-s3-iam-credential-setup` | S3/IAM credential configuration for Excel Query, SFTP, and S3 staging components |

Each skill contains a `SKILL.md` file describing:

- Detection logic
- Refactor rules
- Upgrade guidance
- Validation patterns

---

# 📊 Migration Artifacts

## pipeline_component_inventory.md

Ground truth for **all components across pipelines**.

Contains:

- Pipeline path and component name  
- Component ID and usage count  
- Migration classification (Type 1 / Type 2 / Type 3)  
- Shared pipeline indicators  
- OOM risk scores (when enriched)

Used for:

- Discovery
- Refactor detection
- Validation checks

---

## refactor_components.md

The **single source of truth for refactor work**.

Tracks:

- Workload name  
- Pipeline location  
- Component name  
- Severity (Blocker / Warning / Advisory)  
- Status (Pending / In Progress / Completed)  
- Upgrade reference section  

Refactor behavior:

- Discovered by Maia  
- Performed by the user  
- Tracked and gated here  

---

## validation_reports/

Contains **immutable validation reports** generated during execution testing.

Example:


validation_reports/<WORKLOAD>_Validation_Report.md


Each report contains:

- Execution results
- Detected refactor conditions
- Failure analysis
- Blocker hierarchy
- Root cause analysis
- Recommended next actions

Reports act as **auditable evidence** of migration status.

---

# 🔁 Migration Lifecycle

The migration framework follows a strict sequence.

### 1️⃣ Initialization

- Confirm customer and workload
- Validate required files
- Prepare workspace

### 2️⃣ Discovery (Read-Only)

- Identify shared pipelines
- Identify ingestion systems
- Identify output systems
- Detect refactor conditions

### 3️⃣ Refactor (User-Performed)

- Guided by Maia
- Governed by migration documentation
- Tracked in `refactor_components.md`

### 4️⃣ Validation

- Apply validation rules
- Generate validation report
- Identify remaining blockers

### 5️⃣ Execution

- Run pipelines end-to-end
- **Successful Run is the final authority**

---

# 🚀 Getting Started

1. Clone the repository

```bash
git clone https://github.com/<repo>/Maiaupgrade-Public
```

Read the migration rules

.matillion/maia/rules/migration_manager_instructions.md

Populate:

migration_project/customer_migration_workspace/

Allow Maia to guide the migration workflow.

---

# ⚠️ Governance Principles

This framework enforces strict migration rules:

Discovery is read-only

Refactor is user-performed

Validation never modifies code

Execution results determine completion

All migration decisions must be traceable

These guardrails ensure migrations remain safe, auditable, and repeatable.

---

# Maintainers

Matillion Professional Services
services@matillion.com
