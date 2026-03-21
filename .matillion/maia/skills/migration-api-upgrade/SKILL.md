---
name: migration-api-upgrade
description: Use when refactoring API Extract or API Query components during Matillion ETL to DPC migration.
---

# API Components Migration Guide

## API Extract → Custom Connectors

Reference: https://docs.matillion.com/metl/docs/migration-api-extract/

DPC replaces **API Extract** with **custom connectors**.

### Upgrade Path

1. Export API Extract profiles from Matillion ETL
2. Import profiles into DPC as custom connectors
3. Export/import the job using API Extract
4. Pipeline will reference the custom connector

### Exporting Extract Profiles (Matillion ETL)

1. Click **Project → Manage API Profiles → Manage Extract Profiles**
2. Locate the profile and click download icon
3. Downloads a `.json` file

### Importing to DPC

1. Navigate to DPC
2. Click **Custom Connectors** icon → **Custom Connectors**
3. Click **Import** (top-right)
4. Select the exported `.json` file
5. Click **Import**

### Post-Import Configuration

| Setting | Action Required |
|---------|----------------|
| Name | Keep **same name** as original profile |
| Pagination | **Must reconfigure** (not imported) |
| Authentication | **Must reconfigure** (create new auth config) |
| Parameters | Usually no changes needed |
| Headers | Preserved |
| Request body | Retained |

**Important:** Click **Save** even if no manual changes made.

### Configuring in Pipeline

After importing job:
1. API Extract is replaced with **Custom Connector** component
2. Manual work required:
   - Configure authentication (secrets not imported)
   - Review default values for new properties
   - Update service-specific parameters if environment differs
   - Validate output schema and adjust downstream components

### Platform-Specific Behavior

**Snowflake/Redshift with Load Selected Data = No:**
- Raw JSON staged into VARIANT (Snowflake) or SUPER (Redshift) column
- System auto-unnests first nesting level

**Databricks:**
- Data always loaded according to defined schema
- No implicit flattening

### Feature Comparison

| Feature | API Extract | Custom Connector |
|---------|-------------|------------------|
| Profiles | Matillion ETL config | Imported/created in DPC |
| Pagination | Per endpoint | Per endpoint + script pagination |
| Authentication | In component | Defined once, assigned per endpoint |
| Flattening | Basic JSON | Depends on repeat element config |

---

## API Query Migration

Reference: https://docs.matillion.com/metl/docs/migration-api-query/

> **Requires agent version 10.1232.0+**

### Key Difference

- API Query component **migrates automatically**
- API Query Profile **does NOT migrate** automatically
- Component present but fails validation until profile imported

### Upgrade Path

#### Export Profile (Matillion ETL)

1. Click **Project → Manage API Profiles → Manage Query Profiles**
2. Locate profile and click download icon
3. Exports a `.json` file

> **Tip:** Use Matillion ETL API to download multiple profiles to one `.json`

#### Import Profile (DPC)

1. Open DPC project and branch
2. In **Files** panel:
   - Click `...` next to target folder, **or**
   - Click **Add → Import**
3. Select exported `.json` file
4. Click **Open**
5. In **Importing files**, click **API query profiles** tab
6. Verify expected profiles
7. Profiles appear at: `.matillion/api-query-profiles/<component>/<profile>.rsd`
8. API Query component should now validate

---

---

## DPC-Specific API Query Gotchas

### Performance Regression vs METL

**Severity: 🔴 Critical**

The API Query component in DPC can run **30–100% slower** than the equivalent in METL. This is a confirmed, reproducible issue tied to dispatch overhead in the DPC architecture (not component misconfiguration).

- Tracked as a known product issue (Backlog / Priority 3)
- Affects all API Query executions, not just specific endpoints
- The dispatch tax compounds for pipelines that make many sequential API calls

**Remediation:**
- Batch API calls where possible to reduce total component executions
- Consider Python Pushdown for high-frequency API integrations
- Set customer expectations before migration — this is a known platform difference

### Deprecated Component Breakage Post-Upgrade

**Severity: 🟠 High**

Customers who delayed migration from the old API Query component format may hit **breaking behaviour changes** after upgrading to METL 1.78+. The old profile format is no longer compatible.

**Remediation:**
- Flag early in migration conversations: API Query profiles must be exported and re-imported
- Customers still on old profile format post-1.78 should prioritise the export/import path above
- SOAP API handling (XML-in-CSV responses) has known issues — test thoroughly

---

## Best Practices

1. **Start simple**: Begin with non-authenticated, non-paginated API Extract pipelines
2. **Preview first**: Use custom connector preview to validate config before creating pipelines
3. **Review schemas**: Check data type mappings for discrepancies
4. **Test thoroughly**: Validate output matches expected format
