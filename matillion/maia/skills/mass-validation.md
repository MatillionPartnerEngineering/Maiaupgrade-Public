## Objective
Validate migrated pipelines for correctness and readiness.
Validation does NOT perform refactor.

---

## Inputs
- Workload folder: [FOLDER_NAME]
- component_details.csv
- migration_documentation.md (refactor rule reference only)

---

## Validation Scope

Validate all pipelines for:

1) YAML structure and syntax
2) Missing or invalid configuration
3) Dependency integrity
4) Archived or disabled pipelines
5) Runtime readiness signals

---

## Refactor Detection (Read-Only)

During validation, detect conditions that require refactor.

If detected:
- Update refactor_components.md
- Link to the correct **Upgrade:** section in migration_documentation.md
- Do NOT modify pipeline components

---

## 🧭 Refactor Detection Rules (Authoritative for Detection)

This section defines the **explicit conditions** that require a component to be
added or updated in `refactor_components.md`.

The **refactor method itself** must always be taken from
`migration_documentation.md`.

If a condition below is detected:
- Flag the component
- Assign severity
- Create or update the corresponding entry in `refactor_components.md`
- Link to the referenced section in `migration_documentation.md`
- Do NOT perform the refactor

---

### 1️⃣ Python & Jython Components
**Reference:** `migration_documentation.md → Upgrade: Python`
Also able to be found in component_details.csv in workload filepath

Flag when:
- A **Python Script** component uses **Jython**
- A **Python Script** component uses **Python 2**
- A **Jython** script uses `context.cursor()` or grid variables
- A Python Script relies on a **persistent filesystem**
- Python Script requires packages not available in DPC runtime
- Interpreter type cannot be confirmed via `component_details.csv`

Severity:
- **Blocker**: Jython, Python 2, cursor usage, filesystem dependency
- **Warning**: Interpreter unknown

---

### 2️⃣ Bash Script Components
**Reference:** `migration_documentation.md → Upgrade: Bash scripts`
Also able to be found in component_details.csv in workload filepath

Flag when:
- A **Bash Script** component exists
- Script assumes local VM access
- Script installs OS-level packages
- Script writes to or reads from a persistent filesystem

Severity:
- **Blocker**: Full SaaS without Bash Pushdown
- **Warning**: Hybrid SaaS (manual decision required)

---

### 3️⃣ API Extract Components
**Reference:** `migration_documentation.md → Upgrade: API Extract`
Also able to be found in component_details.csv in workload filepath

Flag when:
- API Extract component is present
- Pagination is configured (not migrated)
- Authentication exists (OAuth / token / key)
- API Extract profiles are referenced

Severity:
- **Blocker**: Authentication required
- **Warning**: Pagination logic present

---

### 4️⃣ API Query Components
**Reference:** `migration_documentation.md → Upgrade: API Query`
Also able to be found in component_details.csv in workload filepath

Flag when:
- API Query component exists
- Query profile is missing post-import
- API Query profile not found in DPC project files

Severity:
- **Blocker**: Missing query profile

---

### 5️⃣ Database Query / JDBC Components
**Reference:** `migration_documentation.md → Upgrade: Database Query`
Also able to be found in component_details.csv in workload filepath

Flag when:
- Database type is not natively supported
- JDBC driver upload is required
- Manifest file is required but missing

Severity:
- **Blocker**: Unsupported database without driver
- **Warning**: Driver present but unvalidated

---

### 6️⃣ dbt Components
**Reference:** `migration_documentation.md → Upgrade: dbt`
Also able to be found in component_details.csv in workload filepath

Flag when:
- Sync File Source component exists
- dbt Core component lacks repository configuration
- dbt version mismatch detected

Severity:
- **Blocker**: Missing repository configuration
- **Warning**: Version mismatch

---

### 7️⃣ Automatic / System Variables
**Reference:** `migration_documentation.md → Upgrade: Automatic variables`

Flag when:
- Unsupported automatic variables are referenced
- Variables require datatype change (UUID vs integer)
- Variables are used directly inside Python or Bash scripts

Severity:
- **Blocker**: Unsupported variables
- **Warning**: Datatype changes required

---

### 8️⃣ Export Variables
**Reference:** `migration_documentation.md → Upgrade: Export variables`

Flag when:
- Component-specific export variables have no DPC equivalent
- Grid return variables are used from child pipelines

Severity:
- **Warning** or **Blocker** depending on dependency depth

---

### 9️⃣ Iterators
**Reference:** `migration_documentation.md → Upgrade: Iterators`
Also able to be found in component_details.csv in workload filepath

Flag when:
- Iterator uses **Stop On Condition = Yes**

Severity:
- **Warning** (manual refactor required)

---

### 🔟 Temporary Tables
**Reference:** `migration_documentation.md → Upgrade: Temporary tables`
Also able to be found in component_details.csv in workload filepath

Flag when:
- Temporary tables are referenced
- Session-bound table assumptions exist

Severity:
- **Blocker**

---

### 1️⃣1️⃣ Extract Nested Data (Databricks)
**Reference:** `migration_documentation.md → Upgrade: Extract Nested Data`

Flag when:
- Extract Nested Data component exists in Databricks projects

Severity:
- **Advisory** (automatic remap expected, verify behavior)

---

### 1️⃣2️⃣ Filter Components (Databricks)
**Reference:** `migration_documentation.md → Upgrade: Filter`

Flag when:
- Filter expressions contain mixed quoting
- Single/double/backtick usage detected

Severity:
- **Warning**

---

### 1️⃣3️⃣ Replicate Components
**Reference:** `migration_documentation.md → Upgrade: Replicate`

Flag when:
- Replicate component exists

Severity:
- **Advisory** (auto-removed, verify connections)

---

### 1️⃣4️⃣ Text Output (Redshift)
**Reference:** `migration_documentation.md → Upgrade: Text Output`

Flag when:
- Text Output component exists
- Row limit per file configured

Severity:
- **Warning**

---

### 1️⃣5️⃣ Transactions
**Reference:** `migration_documentation.md → Upgrade: Transactions`

Flag when:
- Non-supported components are wrapped in transactions
- DDL inside SQL Script within a transaction

Severity:
- **Warning**

---

### 1️⃣6️⃣ Filter with Null Value
**Reference:** `component_details → Filter`

Flag when:
- The Filter is set to null
- There is a blank Value field
- This automatically breaks DPC
- There must be an empty space ( ) in the Value field to successfully run

Severity:
- **Warning**

---

### 1️⃣7️⃣ Connector Authentication
**Reference:** `component_details → [Name of any Connector category component]]`

Flag when:
- There is an unresolved authentication method
- Connectors have one of two authentication methods:
  - **Username & Password** - The password must be Secret created at the project level. If Secret is unresolved, it should be flagged as a warning..
  -- **OAuth** - The OAuth must be a profile created at the Project level. If not already resolved, this should be flagged as a warning.

Severity:
- **Warning**

### 1️⃣8️⃣ Transformation Comments 
- Any transformation that requires some writing of SQL by the user (SQL, Calculator), comments written by the user, denoted with -- have been shown to sometimes break the query as it is passed to Snowflake.
- Condition should be flagged as a warning which can be validated by the user or Maia

---

## 📌 Detection Rules Enforcement

- All detected conditions must be recorded in `refactor_components.md`
- Each entry must include:
  - Component name
  - Location
  - Severity
  - Refactor Guide link (migration_documentation.md anchor)
- Validation must **never** perform refactor
- Refactor guidance must **never** originate from MassValidation.md

---

## Output

Generate:

migration_project/validation_reports/[FOLDER_NAME]_Validation_Report.md

---

## Report Requirements

Include:
- Summary counts
- Validation failures
- Refactor conditions detected
- Pointers to refactor_components.md entries
- No remediation steps beyond documentation links

---

## Enforcement

Validation must NOT:
- Perform refactor
- Change component configuration
- Bypass refactor gating
