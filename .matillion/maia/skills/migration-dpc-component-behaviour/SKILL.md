---
name: migration-dpc-component-behaviour
description: Component behaviour differences between METL and DPC — iterator ordering, Join/CALC drift, agent stability, Git integration, SQS gaps, and other known limitations.
---

# Migration DPC Component Behaviour Differences

## When to Use
- When migrated components produce different results in DPC vs METL
- When iterator ordering or variable binding breaks post-migration
- When agent stability issues (disk, offline, container restart) affect pipelines
- When evaluating DPC feature gaps for migration readiness
- When Git integration issues block development workflow

## Why This Matters
METL and DPC do not have component parity. Several components behave differently in subtle ways that can cause silent data issues or pipeline failures. **Never assume parity — always validate in DPC during migration.**

---

## Iterator Components

### Table Iterator: ORDER BY Not Guaranteed in Advanced Mode

**Severity: 🔴 Critical**

The Table Iterator **does NOT guarantee ORDER BY sequence in Advanced mode**. This is a confirmed bug. Any pipeline relying on ordered iteration must validate this behaviour, especially post-upgrade to 1.78+.

**Remediation:**
- Do not rely on row ordering from Table Iterator Advanced mode
- If order matters, materialise the ordered result to a table first, then iterate
- Validate iteration order during migration testing

### File Iterator Variable Binding Changes

**Severity: 🟠 High**

File Iterator variable bindings changed between METL versions. Project variables that worked in older versions may not resolve correctly post-upgrade to 1.78+. FTP file iterators may throw errors after upgrade.

**Remediation:**
- Test all variable resolution in iterators during upgrade validation
- Re-bind project variables in File Iterator components if errors occur

### Grid Iterator Performance Degradation

**Severity: 🟡 Medium**

Grid Iterator performance can degrade significantly in DPC compared to METL, compounded by the dispatch tax (see migration-dpc-performance skill). Each iteration incurs the full round-trip overhead.

---

## Join Component

**Severity: 🟠 High**

The Join component in DPC has edge cases:
- **NULL key handling** differs from METL
- **Join type defaults** may have changed (LEFT vs INNER) between versions
- Large datasets with no explicit key default to cross-join behaviour

**Remediation:**
- Where possible, push complex joins to Snowflake using a **SQL transformation component**
- Explicitly specify join type and keys — do not rely on defaults
- Validate join output row counts against METL baseline

---

## CALC Component: RANK Mismatch

**Severity: 🟠 High**

The CALC component can produce **different RANK() results** between METL and DPC when:
- Row ordering is non-deterministic (no explicit ORDER BY)
- Ties exist in the ranking key
- Partition boundaries differ due to upstream component output ordering

Results may be **different but valid** — which looks like a bug but is actually ordering non-determinism.

**Remediation:**
- Always add an explicit ORDER BY to RANK expressions
- Include a tiebreaker column to ensure deterministic ordering
- Compare DPC output against METL baseline with explicit ordering

---

## Query Result to Scalar: Fails on Snowflake Shared Views

**Severity: 🟡 Medium**

The Query Result to Scalar component cannot access Snowflake **shared views** (views shared via Snowflake Data Sharing / Marketplace). The DPC agent user needs explicit grants on shared view objects, not just on the sharing database.

**Remediation:**
- Grant explicit SELECT privileges on shared view objects to the DPC execution role
- Test access to shared views before relying on them in production pipelines

---

## Agent Stability

### Disk Exhaustion

**Severity: 🔴 Critical**

Agent disk exhaustion from log accumulation is a real P1 risk for customer-hosted agents with no log rotation configured. Error: `No space left on device`.

**Remediation:**
- Configure log rotation on all customer-hosted agents
- Monitor disk usage proactively
- Set alerts for disk usage thresholds

### Agent Auto-Update Breakage

**Severity: 🟠 High**

Agents on the **"Current" track** can auto-update and break pipelines (driver loss, library loss, behavioural changes).

**Remediation:**
- Pin production agents to the **"Stable" track**
- Test updates on non-production agents before promoting
- Azure Container App agents lose Python libraries on container restart — include libraries in deployment config

### Agent Stuck in Unknown/Pending State

**Severity: 🟠 High**

Agents can get stuck in "Unknown" or "Pending" status, particularly Azure deployments. Usually requires manual intervention (restart, re-register).

---

## Git Integration

### .git Folder Bloat

**Severity: 🟠 High**

`.git` folder bloat is a real operational issue for long-running METL instances. Git walk failures are often triggered by **repository size**, not auth issues — check repo size first.

### Git Walk Failures / Failed to Load Files

**Severity: 🟠 High**

Git-backed pipelines in DPC Designer can fail to load when:
- Branch divergence between local and remote exceeds a threshold
- Merge conflicts exist in pipeline YAML files
- Git provider auth tokens have rotated

**Remediation:**
- Check PAT expiry first; confirm repo-level write access for the Matillion service account
- Enforce branch protection rules to prevent direct commits to main
- Ensure PAT/OAuth tokens for Git integration are on a rotation schedule that includes DPC re-auth
- If persistent, re-publish the pipeline from Designer; check Git branch status

### Git Repository Change Post-Creation

Changing the connected Git repository after project creation is not straightforward. **Choose the correct Git repo at project creation time** — migration between repos is non-trivial.

### Git Configuration Not Automatable via API

**Severity: 🟠 High (Enterprise Blocker)**

Project, environment, agent, user, and secret setup can all be scripted via the DPC API. However, **Git repository attachment cannot be automated** — it requires manual UI steps. This is a product gap for enterprise-scale rollouts with infrastructure-as-code requirements.

### Branches Created Outside DPC Not Visible

Branches created directly in GitHub/GitLab/Bitbucket (outside DPC) are **not automatically surfaced** in the DPC Designer UI. Customers used to METL's Git workflow are surprised by this behaviour.

---

## Post-Processing Errors

**Severity: 🟡 Medium**

"Unable to execute, please contact support" post-processing errors can indicate:
- Resource publication failures (YAML not stored correctly)
- Git sync issues at pipeline commit time
- Agent-side cleanup failures after job completion

Often transient but can become persistent if the Git repo is in a bad state.

**Remediation:**
- Re-publish the pipeline from Designer
- If persistent, check Git branch status and force-push clean pipeline YAML

---

## Known DPC Feature Gaps

### SQS / Event-Driven Orchestration Not Supported

**Severity: 🔴 Critical (Migration Blocker for affected customers)**

DPC does **not** natively support SQS triggers or event-driven orchestration. Customers with SQS-based pipeline triggering cannot migrate without re-architecting their orchestration layer.

**Workaround options:**
- Use DPC's **REST API** to trigger pipelines from an external orchestrator
- Use **AWS Lambda + DPC API** as a proxy for SQS-triggered execution
- Consider **AWS EventBridge → Lambda → DPC API** as a pattern

### SAP ODP Delta Load & Advanced Mode Gaps

**Severity: 🟡 Medium — High-risk for SAP migration customers**

SAP ODP connector in DPC has known issues:
- **Delta load type** not functioning as expected — delta pointer tracking can get out of sync after failed runs
- Full load fallback is not automatic; requires manual delta pointer reset
- **Advanced mode** (SAP Netweaver) is not available in DPC — configuration options present in METL are missing
- Both issues remain open/pending as of early 2026, suggesting product gaps rather than config issues

**Remediation:**
- SAP customers using ODP Delta loads or needing advanced Netweaver configuration should be treated as **high-risk for DPC migration** until these gaps are resolved
- Test delta load behaviour thoroughly in DPC before committing to migration

### Microsoft Exchange: Attachment Downloads

**Severity: 🟡 Medium**

The Microsoft Exchange component in DPC has a known limitation with attachment downloads. Customers using Exchange for email-based file ingestion should validate attachment handling.

### Send Email: Attachment Size Limit

**Severity: 🟡 Medium**

The Send Email component has a hard attachment size limit that is **not configurable**. Customers sending pipeline-generated reports via email should be aware of this ceiling.

### SharePoint REST: Library Hardcoding Regression (v1.80)

**Severity: 🟠 High**

Confirmed regression in v1.80: SharePoint REST Data Transfer hardcodes 'Shared Documents' library. Customers using non-default document libraries will hit this after upgrading from 1.74.

**Remediation:**
- Check if a fix has been released in newer versions before upgrading
- Flag for any SharePoint-using customers before they upgrade past 1.74

---

## SSO / Identity Setup

**Severity: 🔴 Critical — ~20% of all DPC platform cases**

SSO is the highest-volume platform admin issue in DPC. Common failure patterns:

### DNS TXT Record Confusion
Customers frequently don't know which domain(s) to apply the DNS TXT verification record to. Multi-domain organisations are especially prone to this.

**Remediation:** Pre-empt with the DNS entry setup doc early in onboarding.

### Adding New Domains Post-Setup
Adding new allowed email domains requires **Matillion support intervention** — it is not self-service. This is a migration blocker for enterprise orgs onboarding new business units.

**Remediation:** Flag during pre-sales/onboarding scoping. Customers with multi-domain SSO must plan domain additions ahead of time.

### SAML Custom SSO
SAML setup is significantly more complex than OAuth/OIDC. Customers frequently need hands-on assistance.

**Remediation:** Use the SAML SSO docs proactively; offer a setup call for enterprise SAML configurations.

### SSO Session/Token Expiry
Customers don't understand DPC session lifetime and get surprised when tokens expire mid-session.

**Remediation:** Set expectations on session duration during onboarding.

### Okta & Azure Entra Integration
- Both generate recurring support cases
- Azure Entra group sync (SCIM) is a separate concern from SSO login — customers conflate the two
- **Always separate SSO (login) from SCIM (user/group provisioning)** in conversations

---

## SCIM Token Expiry

**Severity: 🟠 High — Silent and Dangerous**

SCIM tokens in DPC **do not auto-rotate**. When they expire, user provisioning silently stops. Customers don't notice until new users can't log in or AD group changes aren't reflected.

There is **no automated notification** when a SCIM token expires.

**Remediation:**
- Set calendar reminders to rotate SCIM tokens before expiry
- Periodically audit SCIM API members vs actual DPC environment members
- Okta app assignment must be at **group level**, not user level, for SCIM to function
- DPC does **not** inherit METL's user/role structure — roles must be reconfigured

---

## Scheduling

### Platform-Level Scheduler Incidents

**Severity: 🔴 Critical**

Platform-wide scheduler failures have been observed where multiple customers report scheduling failures simultaneously. These are platform incidents, not individual configuration issues.

**Remediation:** When multiple customers report scheduling failures at the same time, escalate to SRE immediately as a platform incident.

### Pipeline Stuck in "Running" Status

**Severity: 🟠 High**

Pipelines show as running indefinitely with no error — common symptom of agent connection issues or silent OOM.

**Remediation:** Check agent heartbeat and CloudWatch/agent logs; use the DPC Support Tool to inspect actual execution state.

### Schedule Variable Behaviour

Modifying schedule-related environment variables does not always take effect immediately.

**Remediation:** After updating schedule variables, verify the next run time explicitly in the Schedules UI.

### "Run Now" Disabled

The "Run Now" option can appear greyed out in certain UI states.

**Remediation:** Trigger ad-hoc runs via the Pipeline execution view rather than the Schedules list view.

---

## Roles & Permissions

**Severity: 🟠 High**

### Breaking Changes (Dec 2025 – Feb 2026)

Matillion shipped breaking changes to roles and permissions in three waves (Dec 18, Jan 8, Feb 2026). Change logs were **not published ahead of time**, catching customers off guard.

**Remediation:**
- Proactively alert customers with SCIM/SSO automation or permission-sensitive workflows before any roles/permissions changes ship
- Reference: [Important changes to roles and permissions](https://docs.matillion.com/)

### Workspace vs Project vs Environment Roles

Customers frequently confuse three distinct RBAC layers in DPC:
- **Workspace roles** — top-level org access
- **Project roles** — project-level access
- **Environment roles** — environment-level execution access

Each has different capabilities. Note that variable permission documentation has known gaps.

---

## Custom Connector: No IAM Role Injection

**Severity: 🟠 High (Migration Blocker)**

Custom Connector components in DPC **cannot specify an IAM role** for S3/AWS access. In METL, customers could modify the IAM role per environment. This is a confirmed product gap.

Error: `S3ServiceException: The AWS Access Key Id you provided does not exist in our records (403)`

**Remediation:**
- Use native S3/Redshift components where possible (they support IAM role specification)
- Flag any customer using Custom Connectors to write to S3 as at-risk for this gap
- This has caused customers to pause METL→DPC migrations

---

## Lineage Limitations

**Severity: 🟡 Medium**

DPC lineage has known limitations:
- **Not always complete** — some source tables are missed
- **Stale lineage persists** — deleted components/pipelines remain in lineage with no self-service "reset" option
- SQL is not always surfaced in lineage component properties

**Remediation:**
- Do not position DPC lineage as a full data catalog replacement
- Set expectations around current limitations for customers with strict governance requirements

---

## Streaming / CDC: Cloud Secret Manager Required

**Severity: 🟡 Medium**

DPC Streaming agents **cannot use Matillion-native secret definitions** — they must use cloud provider secret managers (AWS Secrets Manager, GCP Secret Manager).

For GCP streaming deployments:
- Google Secret Manager support is required and non-optional
- Customers must build their own agent deployment templates
- This is **not the same** as DPC's standard secret definitions

**Remediation:** Flag the cloud secret manager dependency upfront for any streaming/CDC customer.

---

## Detection Logic

Flag when any of the following are true:
- Pipeline uses **Table Iterator in Advanced mode** with ORDER BY
- Pipeline uses **File Iterator** with project variables
- Pipeline contains **Join** components with nullable keys
- Pipeline uses **CALC** with RANK/ROW_NUMBER without explicit tiebreaker
- Pipeline uses **Query Result to Scalar** against shared views
- Customer uses **SQS-triggered orchestration** in METL
- Customer uses **SharePoint REST** and is upgrading past 1.74
- Customer uses **SSO/SCIM** for user management
- Customer uses **Custom Connectors** that write to S3/AWS
- Customer has **multi-domain SSO** setup
- Customer uses **SCIM** for user provisioning (token expiry risk)
- Customer has **scheduled pipelines** (platform incident awareness)
- Customer uses **streaming/CDC** on GCP (secret manager dependency)
- Customer has **strict lineage/governance** requirements

## Priority Summary

| Category | Severity | Priority |
|----------|----------|----------|
| Table Iterator ORDER BY not guaranteed | 🔴 Critical | Validate iteration order during testing |
| SQS/event-driven not supported | 🔴 Critical | Architecture decision required pre-migration |
| Agent disk exhaustion | 🔴 Critical | Configure log rotation on all CHA agents |
| SSO setup (DNS, SAML, multi-domain) | 🔴 Critical | Pre-empt with docs during onboarding |
| Platform scheduler incidents | 🔴 Critical | Escalate to SRE when multiple customers affected |
| Custom Connector IAM gap | 🟠 High | Use native components; flag as migration risk |
| SCIM token expiry (silent) | 🟠 High | Set rotation reminders; audit periodically |
| Roles/permissions breaking changes | 🟠 High | Alert customers proactively before changes ship |
| Join component NULL/default drift | 🟠 High | Explicitly specify keys and types |
| CALC RANK mismatch | 🟠 High | Add explicit ORDER BY with tiebreaker |
| File Iterator variable binding changes | 🟠 High | Re-test variable resolution post-upgrade |
| Agent auto-update breakage | 🟠 High | Pin production to Stable track |
| Git walk failures / bloat / API gap | 🟠 High | Check repo size; enforce branch rules |
| SharePoint REST regression (v1.80) | 🟠 High | Check fix availability before upgrade |
| Scheduling stuck runs | 🟠 High | Check agent heartbeat and logs |
| SAP ODP delta + Advanced mode gaps | 🟡 Medium | High-risk for SAP migration customers |
| Lineage: stale and incomplete | 🟡 Medium | Set expectations; not a full catalog replacement |
| Streaming/CDC: cloud secret manager required | 🟡 Medium | Flag GCP dependency upfront |
| Post-processing errors | 🟡 Medium | Re-publish pipeline; check Git state |
| Exchange attachments / Email limits | 🟡 Medium | Validate in trial before migration |