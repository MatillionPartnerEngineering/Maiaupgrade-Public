# Migration Help Guide

This guide helps you get the most out of Maia's migration assistance when moving from Matillion ETL to Data Productivity Cloud (DPC).

---

## Quick Start

### What Can Maia Help With?

| Task | What to Ask |
|------|-------------|
| **Start a migration** | "Initialize migration for [customer name]" |
| **Scan for issues** | "Run refactor discovery on this workload" |
| **Fix a specific component** | "How do I fix this [component type]?" |
| **Validate readiness** | "Validate the [workload] pipelines" |
| **Run execution test** | "Test the [workload] pipeline" |

---

## Getting Targeted Help

Maia has specialized knowledge for different migration scenarios. Ask about specific topics to get detailed guidance.

### Python & Jython Issues

**Ask when you have:**
- Python 2 scripts that need conversion
- Jython scripts using `context.cursor()`
- Scripts that rely on persistent filesystem
- Questions about Python Pushdown vs Python Script

**Example questions:**
- "My Python script uses context.cursor(), how do I fix it?"
- "Should I use Python Pushdown for this workload?"
- "Convert this Jython script to Python 3"
- "What project variables are created for cursor migration?"

---

### API Components

**Ask when you have:**
- API Extract components to migrate
- API Query profile missing errors
- Custom connector configuration questions
- Pagination or authentication setup

**Example questions:**
- "How do I export API Extract profiles?"
- "API Query says profile is missing"
- "Set up authentication for custom connector"
- "Pagination wasn't imported, what do I do?"

---

### Bash Scripts

**Ask when you have:**
- Bash Script components that won't run
- Need to set up Bash Pushdown
- Scripts that install packages or use filesystem

**Example questions:**
- "Convert this Bash Script to Bash Pushdown"
- "Configure SSH connection for Bash Pushdown"
- "My bash script needs to install packages"

---

### Variables

**Ask when you have:**
- Automatic variables that don't exist in DPC
- Export variables without equivalents
- Variable syntax differences
- Grid variable behavior changes

**Example questions:**
- "What's the DPC equivalent of job_id?"
- "Map environment_name to DPC"
- "Export variable 'Iterations Generated' doesn't exist"
- "How do I use thisComponent.rowCount?"

---

### Database Connectors & dbt

**Ask when you have:**
- Database Query components needing JDBC drivers
- dbt Core with Sync File Source
- MySQL driver questions
- Temporary table errors
- Transaction behavior issues

**Example questions:**
- "Database Query needs a driver for [database]"
- "Sync File Source shows as Unknown Component"
- "Configure dbt repository settings"
- "Temporary table not supported error"

---

### Databricks-Specific

**Ask when you have:**
- Extract Nested Data behavior differences
- Filter quoting issues
- Text Output migration (Redshift)

**Example questions:**
- "Extract Nested Data uses Variant instead of Struct"
- "Filter quoting is breaking my query"
- "Migrate Text Output to S3 Unload"

---

## Migration Phases

### Phase 0: Initialization
```
"Initialize migration for [Customer Name] with workload [Workload Name]"
```

### Phase 1: Setup
```
"What secrets need to be created?"
"What assets are required for this migration?"
```

### Phase 2: Discovery
```
"Identify shared pipelines in this project"
"What ingestion systems are used?"
```

### Phase 3: Refactor Discovery
```
"Run refactor discovery" (requires approval)
"Scan for components that need refactoring"
```

### Phase 4: Guided Refactor & Validation
```
"Help me fix the Python cursor issue in [pipeline]"
"Validate the [workload] pipelines"
"Run execution test for [workload]"
```

---

## Understanding Validation Reports

After each validation or execution test, Maia generates a report with:

| Section | What It Shows |
|---------|---------------|
| **Executive Summary** | High-level status and key findings |
| **Primary Blocker** | The first error that must be fixed |
| **Secondary Errors** | Downstream issues caused by the primary blocker |
| **Blocker Hierarchy** | Priority order for fixing issues |
| **Next Actions** | What to do next |

### Blocker Severity

| Severity | Meaning |
|----------|----------|
| **Blocker** | Must fix before pipeline can run |
| **Warning** | Should review, may cause issues |
| **Advisory** | Informational, verify behavior |

---

## Key Files

| File | Purpose |
|------|----------|
| `customer_migration_workspace/[Customer]_Migration_Strategy.md` | Overall progress tracking |
| `customer_migration_workspace/refactor_components.md` | Components needing fixes |
| `customer_migration_workspace/component_details.csv` | Source component inventory |
| `validation_reports/[Workload]_Validation_Report.md` | Per-workload test results |

---

## Tips for Best Results

1. **Be specific** — "Fix the Python cursor in LOAD_CUSTOMER pipeline" works better than "fix Python"
2. **Share error messages** — Copy the exact error text when asking for help
3. **One issue at a time** — Focus on the primary blocker first
4. **Reference the pipeline** — Include pipeline name when asking about specific components
5. **Ask for validation** — Run validation after each fix to verify it worked

---

## Need More Help?

- Ask "What should I do next?" at any point
- Ask "Explain this error: [paste error]" for troubleshooting
- Ask "Show me the refactor status" to see outstanding items
