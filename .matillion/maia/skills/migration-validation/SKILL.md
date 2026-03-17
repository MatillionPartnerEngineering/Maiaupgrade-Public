---
name: migration-validation
description: Use when validating migrated pipelines, detecting refactor conditions, or running mass validation during Matillion ETL to DPC migration.
---

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

### 4️⃣ API Query Components
**Reference:** `migration_documentation.md → Upgrade: API Query`

Flag when:
- API Query component exists
- Query profile is missing post-import
- API Query profile not found in DPC project files

**Severity:**
- **Blocker**: Missing query profile

---

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

### 8️⃣ Export Variables
**Reference:** `migration_documentation.md → Upgrade: Export variables`

Flag when:
- Component-specific export variables have no DPC equivalent
- Grid return variables are used from child pipelines

**Severity:** Warning or Blocker depending on dependency depth

---

### 9️⃣ Iterators
**Reference:** `migration_documentation.md → Upgrade: Iterators`

Flag when:
- Iterator uses **Stop On Condition = Yes**

**Severity:** Warning (manual refactor required)

---

### 🔟 Temporary Tables
**Reference:** `migration_documentation.md → Upgrade: Temporary tables`

Flag when:
- Temporary tables are referenced
- Session-bound table assumptions exist

**Severity:** Blocker

---

### 1️⃣1️⃣ Extract Nested Data (Databricks)
**Reference:** `migration_documentation.md → Upgrade: Extract Nested Data`

Flag when:
- Extract Nested Data component exists in Databricks projects

**Severity:** Advisory (automatic remap expected, verify behavior)

---

### 1️⃣2️⃣ Filter Components (Databricks)
**Reference:** `migration_documentation.md → Upgrade: Filter`

Flag when:
- Filter expressions contain mixed quoting
- Single/double/backtick usage detected

**Severity:** Warning

---

### 1️⃣3️⃣ Replicate Components
**Reference:** `migration_documentation.md → Upgrade: Replicate`

Flag when:
- Replicate component exists

**Severity:** Advisory (auto-removed, verify connections)

---

### 1️⃣4️⃣ Text Output (Redshift)
**Reference:** `migration_documentation.md → Upgrade: Text Output`

Flag when:
- Text Output component exists
- Row limit per file configured

**Severity:** Warning

---

### 1️⃣5️⃣ Transactions
**Reference:** `migration_documentation.md → Upgrade: Transactions`

Flag when:
- Non-supported components are wrapped in transactions
- DDL inside SQL Script within a transaction

**Severity:** Warning

---

### 1️⃣6️⃣ Filter with Null Value

Flag when:
- Filter is set to null or has blank Value field
- **Fix:** Must have an empty space (` `) in the Value field

**Severity:** Warning

---

### 1️⃣7️⃣ Connector Authentication

Flag when:
- Unresolved authentication method exists
- **Username & Password**: Password must be Secret at project level
- **OAuth**: OAuth profile must be created at project level

**Severity:** Warning

---

### 1️⃣8️⃣ Transformation Comments

Flag when:
- SQL or Calculator components contain user comments (`--`)
- Comments have been shown to break queries when passed to Snowflake

**Severity:** Warning (validate manually)

---

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
