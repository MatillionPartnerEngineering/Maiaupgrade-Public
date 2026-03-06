---
name: migration-databricks
description: Use when refactoring Databricks-specific components like Extract Nested Data, Filter quoting issues, or Text Output during Matillion ETL to DPC migration.
---

# Databricks-Specific Migration Guide

## Extract Nested Data → Extract Structured Data

Reference: https://docs.matillion.com/metl/docs/migration-extract-nested-data/

### The Problem

| Platform | Extract Nested Data Uses |
|----------|-------------------------|
| Matillion ETL (Databricks) | **Struct** data type |
| DPC (Databricks) | **Variant** data type |

This causes different behavior between platforms.

### The Solution

DPC provides **Extract Structured Data** component that uses **Struct** type to preserve original behavior.

### Upgrade Mapping

During Databricks migration:
- **Extract Nested Data** (ETL) → **Extract Structured Data** (DPC)
- Ensures equivalent functionality
- Preserves pipeline behavior

> **Note:** DPC does include an Extract Nested Data component for Databricks, but it uses Variant type and is NOT used during migration.

### Scope

This mapping applies **only to Databricks projects**.
- Snowflake: Unaffected
- Amazon Redshift: Unaffected

---

## Filter Component Quoting Issues

Reference: https://docs.matillion.com/metl/docs/upgrade-filter/

Filter components migrate automatically, but **Databricks** has quoting behavior differences.

### The Problem

Databricks Filter components handle quotes differently:
- Single quotes (`'`)
- Double quotes (`"`)
- Backticks (`` ` ``)

### Quoting Behavior Matrix

| Filter Value | Source Type | ETL SQL | DPC SQL | Imported As |
|--------------|-------------|---------|---------|-------------|
| `a` | string/text | `'a'` | `'a'` | `'a'` |
| `'a'` | string/text | `'a'` | `'\''a'\''` | `'a'` |
| `"a"` | string/text | `` `a` `` | `"a"` | `` `a` `` |
| `` `a` `` | string/text | `` `a` `` | `` `a` `` | `` `a` `` |
| `2025-11-24` | datetime | `'2025-11-24'` | `'2025-11-24'` | `'2025-11-24'` |
| `'2025-11-24'` | datetime | `'2025-11-24'` | `'2025-11-24'` | `'2025-11-24'` |
| `1` | numeric | `'1'` | `1` | `1` |
| `'1'` | numeric | `'1'` | `'1'` | `1` |

### Upgrade Path

1. Filter components migrate automatically
2. **Review filter expressions after migration**
3. Verify expressions behave as expected
4. Manual intervention may be required for mixed quoting

---

## Text Output (Amazon Redshift)

Reference: https://docs.matillion.com/metl/docs/migration-text-output/

**Text Output** for Amazon Redshift maps to **S3 Unload** in DPC.

### Property Mapping

| Text Output | S3 Unload | Notes |
|-------------|-----------|-------|
| Schema | Schema | No change |
| Table Name | Table Name | No change |
| S3 URL Location | S3 URL Location | No change |
| S3 Object Prefix | S3 Object Prefix | No change |
| Delimiter | Delimiter | If not comma, sets Data File Type = Delimited |
| Compress Data | Compress Data | No change |
| Null As | NULL As | No change |
| Output Type | Data File Type | If Escaped, sets Escape = Yes |
| Multiple Files | Parallel | Filename behavior differs |
| Row limit per file | *(not migrated)* | Use Max File Size instead |
| Include Header | Include Header | No change |
| Null Handling | *(not migrated)* | Not supported |
| Encryption | Encryption | No change |
| KMS Key ID | KMS Key Id | No change |

### Migration Notes

- S3 Unload **always** appends file number to prefix
- **Row limit per file** not supported → use **Max File Size**
- **Null Handling** not supported

> **Warning:** If **Fixed Width** selected while both Escape and Add quotes are Yes, migration is blocked.

---

## Databricks-Specific Variables

When migrating Jython scripts that use `context.cursor()`, these project variables are created:

**Connection parameters:**
- `mtln_databricks_host`
- `mtln_databricks_http_path` *(must be populated manually)*
- `mtln_databricks_catalog`
- `mtln_databricks_schema`

**Personal access token auth:**
- `mtln_databricks_access_token_secret_name`
- `mtln_databricks_access_token_secret_key`

**OAuth auth:**
- `mtln_databricks_client_id`
- `mtln_databricks_client_secret_secret_name`
- `mtln_databricks_client_secret_secret_key`

> **Important:** `mtln_databricks_http_path` must be populated manually after migration.
