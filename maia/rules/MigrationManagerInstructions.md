# Matillion ETL → Data Productivity Cloud  
## Governed Migration Framework (Maia-Managed)

This repository contains a **governed, auditable framework** for migrating customers from **Matillion ETL** to **Matillion Data Productivity Cloud (DPC)**.

The framework is designed to be operated by **Maia**, Matillion’s Migration Project Manager LLM, and enforces strict separation between:

- **Discovery**
- **Refactor**
- **Validation**
- **Execution**

It supports large-scale, multi-workload migrations with clear gating rules, human oversight, and deterministic outcomes.

---

## 🧠 Primary Entry Point (Read First)

### **MigrationManagerInstructions.md** ⭐

> This file is the **single source of operational truth**.

It defines:
- Maia’s role and authority
- Mandatory project structure
- Phase sequencing and gating
- What Maia *may* and *may not* do
- When user approval is required
- How validation, refactor, and execution interact

**If you read only one file, read this one.**

---

## 📁 Repository Structure

```text
migration_project/
├── _templates_prompt_library/
│   ├── MigrationStrategyandPlanTemplate.md
│   ├── MassValidation.md
│   ├── migration_documentation.md
│
├── customer_migration_workspace/
│   ├── CUSTOMER_MigrationStrategyandPlan.md
│   ├── component_details.csv
│   ├── MAUD.md
│
└── validation_reports/
    ├── <WORKLOAD>_Validation_Report.md
    └── ...
```

## 📘 Core Files Explained

### MigrationManagerInstructions.md  
**Who Maia is and how it behaves**

- Governs all phases of the migration lifecycle
- Enforces read-only discovery and explicit user approval gates
- Prevents silent or implicit refactor
- Controls validation and execution sequencing
- Updates strategy and tracker files automatically
- Maintains the **To Do (Next Actions)** section in the migration plan

This file is the **operational brain** of the framework.

---

### MigrationStrategyandPlan.md  
**The live project ledger**

- Project Progress Dashboard with % progress bars
- Phase-by-phase tracking
- Interactive Workload Migration Tracker
- Explicit gating rules (Blockers, Secrets, Successful Run)
- A concise **To Do (Next Actions)** section actively maintained by Maia

This file answers:

> *“What is the current state of this migration, and what should happen next?”*

---

### migration_documentation.md  
**The refactor authority**

- Lists **every supported and unsupported component type**
- Defines **conditions that require refactor**
- Documents **approved refactor paths**
- Contains all authoritative `Upgrade:` sections:
  - Python / Jython
  - Bash
  - API Extract / API Query
  - Database Query / JDBC
  - dbt
  - Variables / Automatic Variables
  - Iterators
  - Temporary Tables
  - Transactions
  - Text Output
  - Filter (Databricks)
  - Replicate

⚠️ Neither Maia nor users invent refactor logic.  
All refactor guidance must originate from this file.

---

### component_details.csv  
**Ground truth for component presence and location**

Used to:
- Locate components by exact pipeline path
- Detect Python, Jython, Bash, API, dbt, JDBC usage
- Identify shared pipelines
- Identify ingestion and output systems
- Tie refactor findings to concrete, auditable locations

This file powers **both refactor discovery and validation detection**.

---

### refactor_components.md  
**Single source of truth for refactor work**

Every refactor entry includes:
- Workload name
- Component name
- Pipeline location
- Severity: **Blocker / Warning / Advisory**
- Status: **Pending / In Progress / Completed**
- Auto-link to the exact `Upgrade:` section in `migration_documentation.md`
- Referenced secrets (if applicable)

Refactor behavior:
- Discovered by Maia
- Performed by the user
- Tracked and gated here

Validation and execution are **blocked** by unresolved **Blockers**.

---

### MassValidation.md  
**Read-only validation rules**

Validation:
- Never performs refactor
- Detects refactor-required conditions
- Updates `refactor_components.md`
- Generates immutable validation reports

Detection logic explicitly references the conditions defined in
`migration_documentation.md`.

Validation output is **evidence**, not instruction.

---

### validation_reports/  
**Immutable execution evidence**

For each workload execution, Maia generates:

```text
validation_reports/<WORKLOAD>_Validation_Report.md

Each report includes:

- **Validation scope**  
  Pipelines, components, and checks executed as part of the validation run.

- **Failures and warnings**  
  Clear enumeration of blocking errors and non-blocking issues detected during validation.

- **Refactor conditions detected**  
  Any components identified as requiring refactor, aligned to conditions defined in `migration_documentation.md`.

- **Links back to `refactor_components.md`**  
  Direct references to the corresponding refactor ledger entries for traceability and remediation tracking.

- **Clear pass/fail signal**  
  An explicit outcome indicating whether the workload is eligible to proceed toward a Successful Run.
```

Reports are **append-only** and must never be overwritten.

---

## 🔁 How the Framework Is Used (High-Level Flow)

1. **Initialize**  
   - Confirm customer and initial workload  
   - Validate required files are present  

2. **Discovery (Read-Only)**  
   - Shared pipelines and dependencies  
   - Assets and environments  
   - Refactor detection only  

3. **Refactor (User-Performed)**  
   - Guided by Maia  
   - Governed by `migration_documentation.md`  
   - Tracked in `refactor_components.md`  
   - All **Blockers** must be completed before validation  

4. **Validation**  
   - MassValidation rules applied  
   - Validation report generated  
   - Refactor conditions may be *identified* but not fixed  

5. **Execution**  
   - End-to-end pipeline run  
   - **Successful Run** is the final authority for completion  

---

## 🧭 Key Design Principles

- **Discovery ≠ Refactor**
- **Refactor ≠ Validation**
- **Validation ≠ Successful Run**
- **Successful Run is the only completion signal**
- **`refactor_components.md` is the single source of truth**
- **All logic is explicit, documented, and auditable**

---

## 👥 Intended Audience

- Matillion Professional Services  
- Matillion Field Engineering  
- Partner Solution Architects  
- Internal GTM and Migration Specialists  

This framework is designed to scale across:
- Hundreds of pipelines  
- Multiple workloads  
- Multiple environments and cloud providers  

---

## 🚀 Getting Started (Internal Use)

1. Clone this repository  
2. Read **MigrationManagerInstructions.md** first  
3. Copy templates into a new `customer_migration_workspace/`  
4. Upload customer artifacts  
5. Allow Maia to guide the migration  

---

## 📌 Final Note

This repository is **not a script**.  
It is a **governed migration operating model**.

If something is unclear, the answer should already exist in:
- `MigrationManagerInstructions.md`
- `migration_documentation.md`

If it doesn’t, update the framework — **not the rules**.
