---
name: unknown-component-conversion
description: Detect and convert unknown-orchestration components from Matillion ETL (METL) migration back to their proper DPC component types. Covers Excel Query conversion with a complete numeric-to-semantic parameter mapping, and provides an extensible framework for other component types.
---

# Unknown Component Conversion for Migrated Pipelines

## When to Use
- When migrated pipelines contain `type: "unknown-orchestration"` components
- When components appear as (?) icons in the DPC Designer canvas
- When pipeline validation reports unknown component types
- **Every unknown component must be resolved** — no customer can proceed with unknown components in production

## Why This Matters
When pipelines are migrated from METL to DPC, certain component types are not recognized by the migration tooling. These appear as `type: "unknown-orchestration"` in the DPL YAML. The components retain their original parameter values but use **numeric parameter keys** instead of semantic names, making them non-functional in DPC.

Unknown components fall into two categories:
1. **Failed component conversions** — Older or deprecated METL component versions that didn't map to a DPC equivalent. These can be converted by remapping numeric parameters to semantic DPC parameters.
2. **Shared job references** — References to METL shared jobs. These require the shared job mapping feature, not parameter remapping. See `migration-shared-jobs` skill.

---

## Detection

### Step 1: Find All Unknown Components

```
Pattern: type: "unknown-orchestration"
Glob: **/*.orch.yaml
```

Also check for `unknown-transformation` in `.tran.yaml` files (less common).

### Step 2: Identify the Original METL Component Type

The original component type is stored in parameter `"20"`. Common values:

| Parameter "20" Value | DPC Target Component | Component ID |
|---------------------|---------------------|-------------|
| `"Excel"` | Excel Query | `excel-query` |
| `""` (empty) | Unknown — requires manual investigation | — |

If parameter `"20"` contains a value not listed above, investigate the component's other parameters to determine the correct DPC mapping. **Document new mappings in this skill.**

### Step 3: Distinguish Shared Jobs from Component Conversions

| Indicator | Type | Action |
|-----------|------|--------|
| Parameter values containing `Unknown:-` followed by a numeric hash (e.g., `Unknown:-842023425`) | **Shared job reference** | Use `migration-shared-jobs` skill |
| Parameter `"20"` contains a recognizable component type name (e.g., `"Excel"`) | **Component conversion** | Use conversion procedure below |

---

## Conversion: Excel → excel-query

### Complete Parameter Mapping

| Numeric Key | DPC Parameter (dplID) | Description | Required | Notes |
|------------|----------------------|-------------|----------|-------|
| `"1"` | `componentName` | Component display name | Yes | |
| `"2"` | `basicAdvancedMode` | "Basic" or "Advanced" | Yes | |
| `"6"` | `dataSource` | Worksheet/sheet name | Yes (Basic mode) | |
| `"7"` | `dataSelection` | List of columns to load | Yes (Basic mode) | Array of strings |
| `"8"` | `dataSourceFilter` | Filter conditions | No | Grid format |
| `"9"` | `combineFilters` | "And" or "Or" | Yes (Basic mode) | |
| `"10"` | `sqlQuery` | SQL query for Advanced mode | Yes (Advanced mode) | |
| `"11"` | `limit` | Row limit | No | |
| `"12"` | `sortKey` | Sort key columns | No | |
| `"13"` | `targetTable1` | Target table name | Yes | |
| `"14"` | `distributionStyle` | "Even", "Auto", "All", "Key" | Yes | |
| `"15"` | `distributionKey` | Distribution key column | Only if style=Key | |
| `"16"` | `primaryKey` | Primary key columns | No | |
| `"17"` | `schema2` | Target schema | Yes | |
| `"18"` | `encryption` | Encryption method | Yes | Default: "None" |
| `"19"` | — | (Legacy: database reference) | — | Ignore in DPC |
| `"20"` | — | Original METL component type | — | Detection only; do not include in output |
| `"21"` | `loadOptions` | Load options list | No | |
| `"95"` | `useCaching` | Enable caching | No | |
| `"96"` | — | (Legacy: S3 staging path) | — | Ignore |
| `"97"` | — | (Legacy) | — | Ignore |
| `"98"` | — | (Legacy) | — | Ignore |
| `"99"` | `type` | "Standard" or "External" | Yes | |
| `"400"` | `storageUrl` | S3/Azure/GCS URL to .xlsx file | Yes | |
| `"401"` | `cellRange` | Cell range (e.g., "A5:O1000") | No | Basic mode only |
| `"402"` | `containsHeaderRow` | "Yes" or "No" | Yes | |
| `"403"` | `s3StagingArea1` | S3 staging bucket | Yes (Standard type) | |
| `"498"` | `storageType` | "Amazon S3 Storage", "Azure Blob Storage", "Google Cloud Storage" | Yes | |
| `"1001"` | `connectionOptions` | JDBC connection options | No | Grid format |
| `"1013"` | `autoDebug` | "Off" or "On" | Yes | |
| `"1014"` | `debugLevel` | "1" through "5" | Yes (if autoDebug=On) | |
| `"1034"` | — | (Legacy) | — | Ignore |

### Before (unknown-orchestration)

```yaml
    Copy of Template Body-MAR:
      type: "unknown-orchestration"
      transitions:
        success:
        - "Copy of Step-01-fact-JL Legal 1"
        failure:
        - "Copy of SNS Message-08"
      skipped: false
      parameters:
        "1": "Copy of Template Body-MAR"
        "2": "Basic"
        "6": "March"
        "7":
        - "A"
        - "B"
        - "C"
        "8":
        "9": "And"
        "10": ""
        "11": ""
        "12":
        "13": "tmp_legal_body"
        "14": "Even"
        "15": ""
        "16":
        "17": "temp_corp"
        "18": ""
        "20": "Excel"
        "99": "Standard"
        "400": "s3://my-bucket/Legal-Summary.xlsx"
        "401": "A5:O1000"
        "402": "No"
        "403": "[Environment Default]"
        "498": "Amazon S3 Storage"
        "1013": "Off"
        "1014": "3"
      postProcessing:
        updateScalarVariables:
        - - "audit_component"
          - "${sysvar.thisComponent.name}"
        - - "audit_status"
          - "${sysvar.thisComponent.status}"
```

### After (excel-query)

```yaml
    Copy of Template Body-MAR:
      type: "excel-query"
      transitions:
        success:
        - "Copy of Step-01-fact-JL Legal 1"
        failure:
        - "Copy of SNS Message-08"
      skipped: false
      parameters:
        componentName: "Copy of Template Body-MAR"
        basicAdvancedMode: "Basic"
        storageType: "Amazon S3 Storage"
        storageUrl: "s3://my-bucket/Legal-Summary.xlsx"
        containsHeaderRow: "No"
        cellRange: "A5:O1000"
        dataSource: "March"
        dataSelection:
        - "A"
        - "B"
        - "C"
        combineFilters: "And"
        type: "Standard"
        schema2: "temp_corp"
        targetTable1: "tmp_legal_body"
        s3StagingArea1: "[Environment Default]"
        distributionStyle: "Even"
        encryption: "None"
        autoDebug: "Off"
        debugLevel: "3"
      postProcessing:
        updateScalarVariables:
        - - "audit_component"
          - "${sysvar.thisComponent.name}"
        - - "audit_status"
          - "${sysvar.thisComponent.status}"
```

---

## Conversion Procedure

### Step 1: Confirm the Original Type
Check parameter `"20"`. If it equals `"Excel"`, proceed with the excel-query conversion.

### Step 2: Replace the Component Type
```yaml
# Change:
type: "unknown-orchestration"
# To:
type: "excel-query"
```

### Step 3: Remap All Parameters
Using the mapping table above:
1. Convert each numeric key to its semantic DPC parameter name
2. **Drop legacy/ignored parameters**: `"19"`, `"20"`, `"96"`, `"97"`, `"98"`, `"1034"`
3. **Drop empty/null optional parameters** — only include parameters that have values
4. **Preserve transitions and postProcessing** — these are already in correct DPC format
5. **Preserve skipped state** — do not change the `skipped` property

### Step 4: Handle Special Cases
- **Empty `"18"` (encryption)**: Set to `"None"` (the default)
- **Empty `"11"` (limit)**: Omit the parameter entirely (loads all rows)
- **Null `"8"` (dataSourceFilter)**: Omit the parameter (no filters)
- **Null `"1001"` (connectionOptions)**: Omit the parameter
- **Parameter `"401"` (cellRange)**: Only include if non-empty; only applies in Basic mode

### Step 5: Validate
After conversion, run `validate_pipeline` to confirm the component is recognized. Then sample the component to verify data access.

---

## Verification Checklist

- [ ] **Validate**: Run pipeline validation — component should no longer show as unknown
- [ ] **Sample**: Sample the component to confirm it connects and returns data
- [ ] **Check transitions**: Ensure success/failure transitions are preserved and point to valid downstream components
- [ ] **Check postProcessing**: Audit variable mappings should continue to work unchanged
- [ ] **Check design section**: Component positions already exist and do not need to change

---

## Extending This Skill

To add a new conversion mapping for a different component type:

1. Find a working example of the target DPC component (already converted or manually created)
2. Find an `unknown-orchestration` component with the same parameter `"20"` value
3. Compare the two side-by-side to build the numeric-to-semantic mapping
4. Use `get_component_schema` to verify all required parameters for the target component
5. Add a new section to this skill with the mapping table and before/after examples
6. Update the detection table in Step 2 with the new `"20"` value → DPC component mapping

---

## Key Considerations

- **Preserve all transitions** — unknown components already have correct DPC transition structure
- **Preserve postProcessing** — audit variable mappings are in correct format
- **Preserve skipped state** — do not add or remove `skipped` on any component
- **Batch processing** — each component's parameters are unique; process one at a time
- **Component names may contain special characters** — preserve exactly as-is for transition references
- **Design section** — unknown components already have `design.components` entries with positions; these do not need to change