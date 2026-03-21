---
name: migration-hardcoded-credential-detection
description: Detect and remediate hardcoded credentials (passwords, usernames, connection strings) in migrated Matillion ETL pipelines. Identifies plaintext secrets that should be converted to DPC secret references or environment variables.
---

# Hardcoded Credential Detection and Remediation

## When to Use
- After migrating METL pipelines to DPC, before first execution
- When pipeline validation reveals credential-related errors
- When auditing security posture of migrated workloads
- As a companion to the `migration-credentials-audit` skill (which covers the audit methodology; this skill covers detection and fix patterns)

## Why This Matters
Migrated METL pipelines frequently contain **hardcoded credentials** — plaintext passwords, service account usernames, and database connection strings embedded directly in component parameters and version-controlled in YAML. In DPC, these should use **secret references** (`TEXT_SECRET_REF`) and **environment variables** for security and maintainability. Hundreds of hardcoded credential instances per project is typical.

---

## Detection

### Step 1: Detect Hardcoded Passwords

Search for `password:` parameters that contain plaintext values (not secret reference names).

```
# Find all password parameters to audit
Pattern: password:
Glob: **/*.orch.yaml
```

Build an inventory table mapping each hardcoded value to its target system and the correct DPC secret reference name:

| Hardcoded Value | Target System | Correct Secret Reference | Instance Count |
|----------------|---------------|------------------------|----------------|
| `"example_pw"` | Source DB (Production) | `SOURCE_DB_PRD_SEC_DEF` | 24 |
| `"legacy_pw"` | Legacy AS/400 | `LEGACY_PRD_SEC_DEF` | 140+ |
| `""` (empty) | Warehouse / IAM auth | Environment credentials | 30+ |

### Step 2: Detect Hardcoded Usernames

Usernames in `database-query` and `rds-query` components are typically plaintext. While less critical than passwords, they should be documented.

```
Pattern: username:
Glob: **/*.orch.yaml
```

### Step 3: Detect Exposed Connection Strings

```
Pattern: jdbc:
Glob: **/*.orch.yaml
```

Connection strings expose database hostnames and ports. While not credentials themselves, they complete the attack surface when combined with hardcoded passwords.

---

## Remediation

### For Passwords (TEXT_SECRET_REF Parameters)

Replace hardcoded password with the secret reference name:

```yaml
# ❌ BEFORE — Hardcoded password
        password: "my_plaintext_password"

# ✅ AFTER — Secret reference
        password: "MY_SECRET_DEF_NAME"
```

The `password` parameter on `database-query` and `rds-query` components has `dataType: TEXT_SECRET_REF`. DPC resolves the plain string value as a **secret definition name** at runtime.

**Batch fix pattern:**

```yaml
# Use replaceAll: true for each hardcoded value
oldString: 'password: "my_plaintext_password"'
newString: 'password: "MY_SECRET_DEF_NAME"'
replaceAll: true
```

### For Usernames

Usernames can optionally be converted to pipeline variables if they vary by environment:

```yaml
# Option 1: Leave as-is (acceptable for service accounts)
        username: "SVC_BI_READ"

# Option 2: Use variable for environment flexibility
        username: "${db_username}"
```

### For Connection Strings

JDBC URLs should use variables for host/port when environments differ:

```yaml
# Acceptable for single-environment migrations
        connectionUrl: "jdbc:sqlserver://prod-db:1433;databaseName=MyDB"

# Better for multi-environment
        connectionUrl: "jdbc:sqlserver://${db_host}:${db_port};databaseName=${db_name}"
```

---

## Prerequisites

Before replacing hardcoded passwords with secret references:

1. **Verify the secret definition exists** in DPC project settings
2. **If missing**, request the customer create the secret definition with the correct credential value
3. **Use dynamic lookup** on the `password` parameter to see available secret definitions
4. **Map the hardcoded value** to the correct secret using the inventory table

---

## Verification

1. **Search for remaining hardcoded values** — all known plaintext passwords should be replaced
2. **Validate the pipeline** — components should pass validation with secret references
3. **Sample a component** — confirm the secret resolves and the connection succeeds
4. **Run the pipeline** — successful execution confirms end-to-end credential resolution

---

## Key Considerations

- **Never ask for actual password values** — only work with secret reference names
- **Hardcoded passwords that match secret names** may already be correct (verify with lookup)
- **Empty passwords** (`""`) may indicate environment-level authentication (e.g., Redshift IAM) — do not replace with a secret
- **The `secretReferenceNameId` nested format** is a separate issue — see the `secret-reference-fix` skill
- **Batch processing is safe** when the hardcoded value is unique to one secret (use `replaceAll: true`)
- **Secrets that don't exist yet** must be created by the customer — track as customer action items (see `migration-customer-actions` skill)