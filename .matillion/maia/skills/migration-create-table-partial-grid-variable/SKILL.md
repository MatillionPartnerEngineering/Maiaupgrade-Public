# Maiaupgrade Skill: Handle Partial Grid Variable Definitions in Create Table Components

## Skill ID
`maiaupgrade.create-table.partial-grid-variable-normalization`

## Skill Name
Normalize Partial Grid Variable Definitions for DPC Create Table Components

## Objective
Detect and remediate METL-to-DPC migration issues where **Create Table** components use **grid variables** with only a subset of optional column-definition fields populated. In DPC, this can cause execution failure or inconsistent validation behavior unless the full expected column-definition structure is present.

---

## Problem Summary
In METL, a **Create Table** component can successfully use a grid variable that only includes a partial set of column-definition attributes, such as:

- `column_name`
- `data_type`
- `size`
- `position`

Other optional fields may be omitted entirely from the grid variable definition and left unassigned, and the table still creates successfully.

In DPC, the migrated equivalent may fail at runtime with behavior indicating that omitted fields are treated as `null` in a way that is not accepted by the component. Additionally, when a full grid structure is supplied with blank values for optional fields, execution may succeed while validation still shows an error. This creates an inconsistency between **design-time validation** and **runtime execution**.

---

## Symptoms
This skill should be triggered when any of the following are observed after migration:

1. A migrated **Create Table** component fails when driven by a grid variable.
2. The source METL job succeeds, but the DPC version fails.
3. The grid variable defines only a partial subset of column metadata fields.
4. DPC validation reports an error such as:
   - default value is null
   - required column metadata missing
   - invalid grid variable structure
5. A workaround using a “full” grid variable with all expected fields present succeeds at runtime but still shows validation errors.

---

## Root Cause
The DPC Create Table component appears to expect a **fully populated grid schema definition**, or at minimum a grid that includes **all expected column-definition fields**, even when optional fields are intentionally left blank.

This differs from METL behavior, where omitted optional attributes in the grid definition are tolerated.

There are therefore two related issues:

### 1. Functional migration gap
The migrated asset preserves the source logic, but DPC requires a stricter grid structure than METL.

### 2. Validation/runtime inconsistency
When all expected fields are included but optional ones are blank:
- **runtime execution may succeed**
- **component validation may still fail**

---

## Skill Intent
This skill should automatically transform or recommend transformation of partial column-definition grid variables into a **full canonical table-definition grid**, preserving source intent while aligning with DPC expectations.

---

## When to Apply
Apply this skill when all of the following are true:

- Source component is a **Create Table** component
- Column definitions are supplied dynamically via a **grid variable**
- The source grid defines only a subset of available column-definition fields
- DPC migration preserves that partial structure
- DPC validation and/or execution fails or behaves inconsistently

---

## Detection Logic

### Inspect the source job for:
- A Create Table component configured from a grid variable
- A grid variable used to define multiple columns dynamically

### Determine whether the grid variable is partial:
If the grid includes only fields like:
- `column_name`
- `data_type`
- `size`
- `position`

but does **not** include other expected fields supported by DPC table creation, classify it as a **partial column-definition grid**.

## Expected DPC Behavior Assumption

Based on observed behavior during METL → DPC migration testing, the **Create Table** component in DPC appears to enforce stricter requirements for grid-variable-driven column definitions than METL.

### 1. Full Column Definition Schema Expected

When column definitions are supplied dynamically via a **grid variable**, DPC expects the grid schema to include **all supported column-definition fields**, even if those fields are optional.

This means that the grid structure should contain the complete set of attributes used by the Create Table component, such as:

- `column_name`
- `data_type`
- `size`
- `position`
- `nullable`
- `default_value`
- `precision`
- `scale`
- `primary_key`
- `unique`
- `description`

While some of these attributes may be optional from a logical perspective, DPC appears to require their **presence in the grid schema**.

---

### 2. Field Presence vs Field Value

DPC distinguishes between:

| Condition | Behavior |
|---|---|
| Field **not present** in grid schema | May trigger runtime or validation errors |
| Field present but **blank/empty** | Usually accepted during execution |

Therefore, optional attributes should generally be **defined in the grid structure but left empty** when not needed.

Example acceptable pattern:

| column_name | data_type | size | position | nullable | default_value |
|---|---|---|---|---|---|
| C1 | VARCHAR | 20 | 1 | | |
| C2 | INTEGER | | 2 | | |

---

### 3. Validation vs Runtime Inconsistency

Current behavior suggests that:

- **Component validation may flag errors** when optional fields are blank
- **Runtime execution may still succeed**

This creates a scenario where:

| Stage | Result |
|---|---|
| Component validation | Error or warning |
| Job execution | Successful table creation |

Migration tooling should therefore treat **runtime execution as authoritative** when optional metadata fields are intentionally blank.

---

### 4. Behavioral Difference from METL

In METL, the Create Table component allows grid variables to define **only the subset of fields actively used**, such as:

- `column_name`
- `data_type`
- `size`
- `position`

All other attributes can be omitted entirely without affecting execution.

In DPC, however, omitted fields may implicitly evaluate to **null in a way that the component does not accept**, leading to failures unless the fields are explicitly included.

---

### 5. Migration Implication

To maintain compatibility when migrating jobs that dynamically define columns:

- Grid variables should be **expanded to the full Create Table schema**
- Optional attributes should be **included but left blank**
- Migration logic should normalize partial schemas before execution

This approach preserves the source behavior while satisfying DPC's stricter schema expectations.