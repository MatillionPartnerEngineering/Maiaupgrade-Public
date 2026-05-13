---
name: migration-validation
description: Use when validating migrated pipelines, detecting refactor conditions, or running mass validation during Matillion ETL to DPC migration.
schema_version: 1
phases:
  - discovery
  - validation
detection_rules:
  - id: python-jython
    title: Python & Jython Components
    reference: "migration_documentation.md → Upgrade: Python"
    body_anchor: python-jython
    severity: blocker
    applies_when:
      component_types: [python-script]
  - id: bash-script
    title: Bash Script Components
    reference: "migration_documentation.md → Upgrade: Bash scripts"
    body_anchor: bash-script
    severity: blocker
    applies_when:
      component_types: [bash-script]
  - id: api-extract
    title: API Extract Components
    reference: "migration_documentation.md → Upgrade: API Extract"
    body_anchor: api-extract
    severity: blocker
    applies_when:
      component_types: [api-extract]
  - id: api-query
    title: API Query Components
    reference: "migration_documentation.md → Upgrade: API Query"
    body_anchor: api-query
    severity: blocker
    applies_when:
      component_types: [api-query]
  - id: database-query-jdbc
    title: Database Query / JDBC Components
    reference: "migration_documentation.md → Upgrade: Database Query"
    body_anchor: database-query-jdbc
    severity: blocker
    applies_when:
      component_types: [database-query]
  - id: dbt
    title: dbt Components
    reference: "migration_documentation.md → Upgrade: dbt"
    body_anchor: dbt
    severity: blocker
    applies_when:
      component_types: [sync-file-source, dbt-core]
  - id: automatic-system-variables
    title: Automatic / System Variables
    reference: "migration_documentation.md → Upgrade: Automatic variables"
    body_anchor: automatic-system-variables
    severity: blocker
    applies_when:
      signals: [automatic-variable-reference]
  - id: export-variables
    title: Export Variables
    reference: "migration_documentation.md → Upgrade: Export variables"
    body_anchor: export-variables
    severity: blocker
    applies_when:
      signals: [export-variable, grid-return-variable]
  - id: iterators
    title: Iterators
    reference: "migration_documentation.md → Upgrade: Iterators"
    body_anchor: iterators
    severity: warning
    applies_when:
      component_types: [iterator]
      signals: [stop-on-condition]
  - id: temporary-tables
    title: Temporary Tables
    reference: "migration_documentation.md → Upgrade: Temporary tables"
    body_anchor: temporary-tables
    severity: blocker
    applies_when:
      signals: [temporary-table-reference]
  - id: extract-nested-data-databricks
    title: Extract Nested Data (Databricks)
    reference: "migration_documentation.md → Upgrade: Extract Nested Data"
    body_anchor: extract-nested-data-databricks
    severity: advisory
    applies_when:
      component_types: [extract-nested-data]
      project_types: [databricks]
  - id: filter-databricks
    title: Filter Components (Databricks)
    reference: "migration_documentation.md → Upgrade: Filter"
    body_anchor: filter-databricks
    severity: warning
    applies_when:
      component_types: [filter]
      project_types: [databricks]
  - id: replicate
    title: Replicate Components
    reference: "migration_documentation.md → Upgrade: Replicate"
    body_anchor: replicate
    severity: advisory
    applies_when:
      component_types: [replicate]
  - id: text-output-redshift
    title: Text Output (Redshift)
    reference: "migration_documentation.md → Upgrade: Text Output"
    body_anchor: text-output-redshift
    severity: warning
    applies_when:
      component_types: [text-output]
      project_types: [redshift]
  - id: transactions
    title: Transactions
    reference: "migration_documentation.md → Upgrade: Transactions"
    body_anchor: transactions
    severity: warning
    applies_when:
      signals: [transaction-block]
  - id: filter-null-value
    title: Filter with Null Value
    reference: "migration_documentation.md → Upgrade: Filter"
    body_anchor: filter-null-value
    severity: warning
    applies_when:
      component_types: [filter]
      signals: [null-value-field, blank-value-field]
  - id: connector-authentication
    title: Connector Authentication
    reference: ".matillion/maia/skills/migration-secrets/SKILL.md"
    body_anchor: connector-authentication
    severity: warning
    applies_when:
      signals: [connector-authentication]
  - id: transformation-comments
    title: Transformation Comments
    reference: "migration_documentation.md → Upgrade: SQL comments"
    body_anchor: transformation-comments
    severity: warning
    applies_when:
      component_types: [sql-script, calculator]
      signals: [sql-line-comment]
  - id: create-table-partial-grid-variable
    title: Create Table Partial Grid Variable
    reference: ".matillion/maia/skills/migration-create-table-partial-grid-variable/SKILL.md"
    body_anchor: create-table-partial-grid-variable
    severity: blocker
    applies_when:
      component_types: [create-table]
      signals: [partial-grid-variable]
---

> **Schema migration note (`schema_version: 1`)**: every detection rule documented in the body is now promoted to structured `detection_rules`. See `.matillion/maia/SCHEMA.md` for the contract.

# Migration Validation Skill

Validate migrated pipelines for correctness and readiness. **Validation does NOT perform refactor.**

## Inputs Required
- Workload folder name
- component_details.csv
- Individual skill SKILL.md files (authoritative refactor guidance per condition)
- `migration_documentation.md` (fallback reference when no dedicated skill exists)

## Skill Cross-Reference

Each detection rule maps to a dedicated skill that provides the refactor guidance. When a condition is detected, the corresponding skill is activated during Phase 4 refactor.

| Detection Rule | Skill Path | Skill Purpose |
|----------------|-----------|---------------|
| 1. Python & Jython | `.matillion/maia/skills/migration-python/SKILL.md` | Python 2→3, Jython cursor, Python Pushdown |
| 2. Bash Script | `.matillion/maia/skills/migration-bash/SKILL.md` | Bash Pushdown configuration, SSH setup |
| 3. API Extract | `.matillion/maia/skills/migration-api-upgrade/SKILL.md` | Custom connector setup, profile export/import |
| 4. API Query | `.matillion/maia/skills/migration-api-upgrade/SKILL.md` | Custom connector setup, profile export/import |
| 5. Database Query / JDBC | `.matillion/maia/skills/migration-database-query/SKILL.md` + `.matillion/maia/skills/migration-connectors/SKILL.md` | Driver compatibility, JDBC upload |
| 6. dbt | `.matillion/maia/skills/migration-dbt/SKILL.md` | Repository config, Sync File Source removal |
| 7. Automatic / System Variables | `.matillion/maia/skills/migration-automatic-variables/SKILL.md` | System variable syntax mapping |
| 8. Export Variables | `.matillion/maia/skills/migration-variables/SKILL.md` | Variable type mapping (env, job, grid) |
| 9. Iterators | `.matillion/maia/skills/migration-variables/SKILL.md` | Iterator behavior differences |
| 10. Temporary Tables | `migration_documentation.md → Upgrade: Temporary tables` | No dedicated skill — use documentation |
| 11. Extract Nested Data (Databricks) | `.matillion/maia/skills/migration-databricks/SKILL.md` | Databricks-specific migration |
| 12. Filter (Databricks) | `.matillion/maia/skills/migration-databricks/SKILL.md` | Databricks quoting differences |
| 13. Replicate | `migration_documentation.md → Upgrade: Replicate` | No dedicated skill — use documentation |
| 14. Text Output (Redshift) | `migration_documentation.md → Upgrade: Text Output` | No dedicated skill — use documentation |
| 15. Transactions | `migration_documentation.md → Upgrade: Transactions` | No dedicated skill — use documentation |
| 16. Filter with Null Value | `migration_documentation.md` | Core DPC concern |
| 17. Connector Authentication | `.matillion/maia/skills/migration-secrets/SKILL.md` | Recreate secrets in DPC |
| 18. Transformation Comments | `migration_documentation.md` | Core DPC concern |
| 19. Create Table Partial Grid Variable | `.matillion/maia/skills/migration-create-table-partial-grid-variable/SKILL.md` | Expand partial grid variables to full schema |

## Validation Scope

Validate all pipelines for:
1. YAML structure and syntax
2. Missing or invalid configuration
3. Dependency integrity
4. Archived or disabled pipelines
5. Runtime readiness signals

## Refactor Detection (Read-Only)

During validation, detect conditions that require refactor. If detected:
- Update `refactor_components.md`
- Link to the correct **Upgrade:** section in migration_documentation.md
- **Do NOT modify pipeline components**

---

## Detection Rules

<a id="python-jython"></a>
### 1️⃣ Python & Jython Components
**Reference:** `migration_documentation.md → Upgrade: Python`

Flag when:
- Python Script uses **Jython** or **Python 2**
- Jython script uses `context.cursor()` or grid variables
- Python Script relies on persistent filesystem
- Python Script requires packages not available in DPC runtime
- Interpreter type cannot be confirmed via component_details.csv

**Severity:**
- **Blocker**: Jython, Python 2, cursor usage, filesystem dependency
- **Warning**: Interpreter unknown

---

<a id="bash-script"></a>
### 2️⃣ Bash Script Components
**Reference:** `migration_documentation.md → Upgrade: Bash scripts`

Flag when:
- Bash Script component exists
- Script assumes local VM access
- Script installs OS-level packages
- Script writes to/reads from persistent filesystem

**Severity:**
- **Blocker**: Full SaaS without Bash Pushdown
- **Warning**: Hybrid SaaS (manual decision required)

---

<a id="api-extract"></a>
### 3️⃣ API Extract Components
**Reference:** `migration_documentation.md → Upgrade: API Extract`

Flag when:
- API Extract component is present
- Pagination is configured (not migrated)
- Authentication exists (OAuth / token / key)
- API Extract profiles are referenced

**Severity:**
- **Blocker**: Authentication required
- **Warning**: Pagination logic present

---

<a id="api-query"></a>
### 4️⃣ API Query Components
**Reference:** `migration_documentation.md → Upgrade: API Query`

Flag when:
- API Query component exists
- Query profile is missing post-import
- API Query profile not found in DPC project files

**Severity:**
- **Blocker**: Missing query profile

---

<a id="database-query-jdbc"></a>
### 5️⃣ Database Query / JDBC Components
**Reference:** `migration_documentation.md → Upgrade: Database Query`

Flag when:
- Database type is not natively supported
- JDBC driver upload is required
- Manifest file is required but missing

**Severity:**
- **Blocker**: Unsupported database without driver
- **Warning**: Driver present but unvalidated

---

<a id="dbt"></a>
### 6️⃣ dbt Components
**Reference:** `migration_documentation.md → Upgrade: dbt`

Flag when:
- Sync File Source component exists
- dbt Core component lacks repository configuration
- dbt version mismatch detected

**Severity:**
- **Blocker**: Missing repository configuration
- **Warning**: Version mismatch

---

<a id="automatic-system-variables"></a>
### 7️⃣ Automatic / System Variables
**Reference:** `migration_documentation.md → Upgrade: Automatic variables`

Flag when:
- Unsupported automatic variables are referenced
- Variables require datatype change (UUID vs integer)
- Variables are used directly inside Python or Bash scripts

**Severity:**
- **Blocker**: Unsupported variables
- **Warning**: Datatype changes required

---

<a id="export-variables"></a>
### 8️⃣ Export Variables
**Reference:** `migration_documentation.md → Upgrade: Export variables`

Flag when:
- Component-specific export variables have no DPC equivalent
- Grid return variables are used from child pipelines

**Severity:** Warning or Blocker depending on dependency depth

---

<a id="iterators"></a>
### 9️⃣ Iterators
**Reference:** `migration_documentation.md → Upgrade: Iterators`

Flag when:
- Iterator uses **Stop On Condition = Yes**

**Severity:** Warning (manual refactor required)

---

<a id="temporary-tables"></a>
### 🔟 Temporary Tables
**Reference:** `migration_documentation.md → Upgrade: Temporary tables`

Flag when:
- Temporary tables are referenced
- Session-bound table assumptions exist

**Severity:** Blocker

---

<a id="extract-nested-data-databricks"></a>
### 1️⃣1️⃣ Extract Nested Data (Databricks)
**Reference:** `migration_documentation.md → Upgrade: Extract Nested Data`

Flag when:
- Extract Nested Data component exists in Databricks projects

**Severity:** Advisory (automatic remap expected, verify behavior)

---

<a id="filter-databricks"></a>
### 1️⃣2️⃣ Filter Components (Databricks)
**Reference:** `migration_documentation.md → Upgrade: Filter`

Flag when:
- Filter expressions contain mixed quoting
- Single/double/backtick usage detected

**Severity:** Warning

---

<a id="replicate"></a>
### 1️⃣3️⃣ Replicate Components
**Reference:** `migration_documentation.md → Upgrade: Replicate`

Flag when:
- Replicate component exists

**Severity:** Advisory (auto-removed, verify connections)

---

<a id="text-output-redshift"></a>
### 1️⃣4️⃣ Text Output (Redshift)
**Reference:** `migration_documentation.md → Upgrade: Text Output`

Flag when:
- Text Output component exists
- Row limit per file configured

**Severity:** Warning

---

<a id="transactions"></a>
### 1️⃣5️⃣ Transactions
**Reference:** `migration_documentation.md → Upgrade: Transactions`

Flag when:
- Non-supported components are wrapped in transactions
- DDL inside SQL Script within a transaction

**Severity:** Warning

---

<a id="filter-null-value"></a>
### 1️⃣6️⃣ Filter with Null Value

Flag when:
- Filter is set to null or has blank Value field
- **Fix:** Must have an empty space (` `) in the Value field

**Severity:** Warning

---

<a id="connector-authentication"></a>
### 1️⃣7️⃣ Connector Authentication

Flag when:
- Unresolved authentication method exists
- **Username & Password**: Password must be Secret at project level
- **OAuth**: OAuth profile must be created at project level

**Severity:** Warning

---

<a id="transformation-comments"></a>
### 1️⃣8️⃣ Transformation Comments

Flag when:
- SQL or Calculator components contain user comments (`--`)
- Comments have been shown to break queries when passed to Snowflake

**Severity:** Warning (validate manually)

---

<a id="create-table-partial-grid-variable"></a>
### 1️⃣9️⃣ Create Table Partial Grid Variable
**Reference:** `.matillion/maia/skills/migration-create-table-partial-grid-variable/SKILL.md`

Flag when:
- Create Table component uses a grid variable for column definitions
- Grid variable contains only partial fields (e.g., `column_name`, `data_type`, `size`, `position`) instead of the full DPC schema
- Missing optional fields cause runtime execution failure despite validation passing

**Severity:**
- **Blocker**: Runtime failure — partial grid variables must be expanded to include all column-definition fields (even if blank)

---

## Output Requirements

Generate validation report at:
```
migration_project/validation_reports/[WORKLOAD]_Validation_Report.md
```

**Report must include:**
- Summary counts
- Validation failures
- Refactor conditions detected
- Pointers to refactor_components.md entries
- No remediation steps beyond documentation links

## Enforcement Rules

Validation must **NOT**:
- Perform refactor
- Change component configuration
- Bypass refactor gating

All detected conditions must be recorded in `refactor_components.md` with:
- Component name
- Location
- Severity
- Refactor Guide link (migration_documentation.md anchor)
