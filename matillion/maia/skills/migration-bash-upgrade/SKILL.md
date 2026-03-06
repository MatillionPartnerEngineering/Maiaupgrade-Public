---
name: migration-bash-upgrade
description: Use when refactoring Bash Script or converting to Bash Pushdown during Matillion ETL to DPC migration.
---

# Bash Scripts Migration Guide

Reference: https://docs.matillion.com/metl/docs/migration-bash/

## Overview

**Bash Script** components automatically import but may require refactor. Unlike Matillion ETL (runs on your Linux VM), DPC uses a SaaS model with no underlying VM.

## Upgrade Options

### Option 1: Bash Pushdown (Recommended)

Run Bash scripts on a Linux VM you provide and connect to via SSH.

**Advantages:**
- Set CPU and memory as needed
- Install packages/third-party applications
- Full control over execution environment

**Considerations:**
- You must manage, secure, and update the Linux VM
- Network access required from DPC agent to VM

### Option 2: Native Component Replacement

Check if functionality has a native component equivalent:
- **Print Variables** for debugging output
- Other native components for file operations

### Option 3: Python Pushdown (Snowflake Only)

If workload can be written in Python instead.

### Option 4: Python Script (Hybrid SaaS Only)

If workload can be rewritten in Python.

### Option 5: Keep Bash Script (Not Recommended)

- Won't run in **Full SaaS**
- May run with problems in **Hybrid SaaS**
- Contact Matillion Support if needed

---

## Converting to Bash Pushdown

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

## Common Refactor Scenarios

| Original Bash Usage | Recommended Approach |
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
