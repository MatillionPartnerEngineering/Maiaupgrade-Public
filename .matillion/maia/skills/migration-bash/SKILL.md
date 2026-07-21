---
name: migration-bash
description: Use when migrating Bash Script components to DPC. Bash scripts migrate automatically via the Script Pushdown component on the Shared Script Runner; manual refactoring (or bring-your-own-VM Bash Pushdown) is the exception.
schema_version: 1
phases:
  - refactor
  - validation
detection_rules:
  - id: bash-script-migration
    title: Bash Script component migration
    reference: "https://docs.matillion.com/metl/docs/migration-bash/"
    body_anchor: bash-script-migration
    severity: blocker
    applies_when:
      component_types: [bash-script]
---

<a id="bash-script-migration"></a>
# Bash Scripts Migration Guide

Reference: https://docs.matillion.com/metl/docs/migration-bash/

## Overview

**Bash Script** components migrate **automatically**. The migration converts them to the **Script Pushdown** component, which executes on the managed **Shared Script Runner** — a Matillion-managed Linux environment. No bring-your-own-VM setup or manual refactor is required by default.

Manual refactoring is now the **exception**, not the rule — reserve it for the specific cases called out below (e.g. scripts that depend on OS-level packages the Shared Script Runner does not provide, or that need custom CPU/memory beyond the shared runner's limits).

Reference:
- Script Pushdown component: https://docs.maia.ai/docs/components/script-pushdown#script-pushdown
- Shared Script Runner: https://docs.maia.ai/docs/guides/shared-script-runner

## Default path: Script Pushdown on the Shared Script Runner

Bash Script components are automatically migrated to **Script Pushdown** and run on the **Shared Script Runner**. This is the recommended path for the vast majority of Bash scripts and requires no manual work.

**Why this is the default:**
- Fully automatic during migration — no per-script conversion decision needed.
- Runs on a Matillion-managed Linux environment (no VM for you to provision, secure, or patch).
- Preserves standard shell behaviour for typical scripting (file staging, CLI tools, orchestration glue).

## Exceptions — when manual attention is still needed

Consider one of the alternatives below only when the default path genuinely does not fit:

### Alternative 1: Bring-your-own-VM Bash Pushdown

Run Bash scripts on a Linux VM you provide and connect to via SSH. Use this only when you need OS-level packages/applications not available on the Shared Script Runner, or CPU/memory beyond the shared runner's limits.

**Advantages:**
- Set CPU and memory as needed
- Install packages/third-party applications
- Full control over execution environment

**Considerations:**
- You must manage, secure, and update the Linux VM
- Network access required from DPC agent to VM

### Alternative 2: Native Component Replacement

Where a script only did something a native component already does, replacing it can be cleaner:
- **Print Variables** for debugging output
- Other native components for file operations

### Alternative 3: Python Pushdown (Snowflake Only)

If the workload is better expressed in Python and the project is on Snowflake.

### Alternative 4: Python Script (Hybrid SaaS Only)

If the workload is better rewritten in Python on a Hybrid SaaS agent.

---

## Converting to bring-your-own-VM Bash Pushdown (exception path)

Only needed for Alternative 1 above — the default Script Pushdown / Shared Script Runner path requires none of these steps.

### Steps

1. Click **Edit preferences** in **Importing files** panel
2. Toggle **Convert to Bash Pushdown** to **On** (default Off)
3. Configure connection parameters:

| Parameter | Description |
|-----------|-------------|
| **Host** | Hostname or IP address |
| **User Name** | SSH username |
| **Connection Timeout (ms)** | Default 3000 |
| **Port** | Default 22 |
| **Authentication Type** | Password or Key Pair |

**For Password authentication:**
- Select a secret containing the password

**For Key Pair authentication:**
- Select a secret containing the private key
- If passphrase protected: Set **Require Passphrase = Yes**, select passphrase secret

4. Click **Apply & re-run**
5. Migration report shows: "Bash Script component has been converted to a Bash Pushdown component."
6. Click **Import**

---

## Automatic Variables in Bash

DPC doesn't support directly accessing automatic variables through **Bash Script**.

**Workaround:**
1. Use **Update Scalar** component to write values to user-defined variables
2. Pass those variables to the Bash script

---

## Optional refactor scenarios

These are **optional** improvements, not required migration steps — the default Script Pushdown path already runs Bash scripts as-is. Consider them only if you are actively simplifying a pipeline.

| Original Bash Usage | Optional alternative |
|---------------------|---------------------|
| Print debug info | Use **Print Variables** component |
| File operations | Use native file components |
| API calls | Consider **API Query** or **Custom Connector** |
| Database operations | Use **Python Pushdown** (Snowflake) |
| Package installation | Use **Bash Pushdown** with managed VM |
| Persistent file storage | Use cloud storage (S3/Azure Blob) |

---

## Secrets for Bash Pushdown

Read **Secrets and secret definitions** documentation to create secrets for:
- SSH passwords
- Private keys
- Key passphrases

See **Bash Pushdown** documentation for additional configuration properties.
