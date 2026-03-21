---
name: migration-rds-query-validation
description: Detect and remediate structural validation errors in rds-query components migrated from Matillion ETL to DPC. Covers skipped component validation, credential conversion, and the validation-vs-runtime inconsistency.
---

# RDS Query Structural Validation

## When to Use
- When migrated pipelines contain `rds-query` components with validation errors
- When API-based pipeline edits fail due to structural errors on skipped components
- When `rds-query` components need credential conversion to secret references

## Why This Matters
Migrated `rds-query` components can exhibit **structural validation errors** in DPC that prevent API-based modifications to the pipeline. These errors are distinct from credential issues — they relate to how the component's connections and parameters are structured in the DPL YAML. The most common issue is validation errors on **skipped components** that create invalid transition chains.

---

## Detection

### Step 1: Find All rds-query Components

```
Pattern: type: "rds-query"
Glob: **/*.orch.yaml
```

### Step 2: Validate Pipelines

Run `validate_pipeline` on each file. Look for errors such as:
- `"single source connection"` — structural connection issue
- `"Invalid option"` — parameter value not in allowed set
- `"Input required"` — missing required parameter

### Step 3: Identify Skipped rds-query Components

Cross-reference `type: "rds-query"` with `skipped: true`. Skipped components often trigger validation errors even though they won't execute.

---

## Root Cause: Skipped Component Validation

DPC validates **all components** regardless of `skipped` state. A skipped `rds-query` component with invalid parameters will:
1. Generate validation errors
2. May prevent API-based edits to **other components** in the same pipeline
3. Block automated remediation workflows

This creates a circular problem: you need to fix the skipped component to enable API edits, but the component is skipped because it's not needed.

---

## Known Structural Issues

### Issue 1: Invalid Transition Chains Through Skipped Components

**Symptom:** Validation error `"single source connection"` on skipped components.

**Cause:** Skipped components are connected in sequence, but their parameters are invalid. DPC validates the entire chain.

### Issue 2: Missing or Empty Credential Parameters

**Symptom:** `rds-query` components with empty `password` fields or hardcoded values.

```yaml
# ❌ Empty password (common in migrated rds-query)
        password: ""

# ❌ Hardcoded password
        password: "plaintext_password"

# ✅ Correct — secret reference
        password: "MY_DB_SECRET_DEF"
```

### Issue 3: Parameter Format Differences

Some `rds-query` parameters have different formatting requirements in DPC vs METL:
- `connectionUrl` — must be a valid JDBC URL
- `sqlQuery` — may need syntax adjustments for the target database
- `columnNames` — list format may differ

---

## Remediation

### Option A: Fix Parameters on Skipped Components (Preferred)

Even though the component won't execute, fix its parameters to satisfy validation. This unblocks API-based edits to the rest of the pipeline.

```yaml
    Skipped Component:
      type: "rds-query"
      skipped: true  # Keep skipped
      parameters:
        componentName: "Skipped Component"
        password: "MY_DB_SECRET_DEF"  # Fix credentials even on skipped components
```

### Option B: Manual Fix in Designer UI

If API-based fixes fail due to structural errors:
1. Open the pipeline in the Designer UI
2. Click on the skipped rds-query component
3. Fix the credential and connection parameters via the UI
4. Save — this writes the correct DPL format

### Option C: Remove Skipped Components (If Confirmed Unused)

If the customer confirms the skipped components are permanently decommissioned:
1. Remove the component from `pipeline.components`
2. Remove from `design.components`
3. Remove all transition references to/from the component
4. Update upstream/downstream transitions to bypass the removed component

⚠️ **Always confirm with the customer** before removing components.

---

## rds-query vs database-query

| Feature | `rds-query` | `database-query` |
|---------|------------|------------------|
| Connection | JDBC URL + credentials in component | Named connection reference |
| Use case | Direct RDS/external DB queries | Queries via pre-configured connections |
| Credential format | `password` as `TEXT_SECRET_REF` | `password` as `TEXT_SECRET_REF` |
| `concurrencyMethod` | Not applicable | Required ("Absolute" or "STV_SLICES") |
| Migration issues | Structural validation + credentials | Credentials + concurrencyMethod |

---

## Validation vs Runtime Inconsistency

| Stage | Behavior |
|-------|----------|
| Component validation | Validates ALL components including skipped ones |
| Pipeline execution | Skips components with `skipped: true` |
| API edits | May be blocked if ANY component has validation errors |

**Implication:** Even non-executing components must have valid-enough parameters to pass validation. This is a DPC behavioral requirement with no METL equivalent.

---

## Verification

1. **Validate the pipeline** — all components (including skipped) should pass validation
2. **Sample active rds-query components** — confirm connection and query execution
3. **Check transition integrity** — verify all transitions point to existing components
4. **Run the pipeline** — skipped components should be bypassed cleanly

---

## Key Considerations

- **Skipped rds-query components block API automation** — fix them first to enable batch remediation
- **Structural errors may require manual UI fixes** when API edits fail
- **rds-query credentials work identically to database-query** — plain string secret reference format
- **Do not unskip components** without customer confirmation — they may be intentionally disabled
- **Transition chains through skipped components are valid** — DPC handles the flow correctly at runtime