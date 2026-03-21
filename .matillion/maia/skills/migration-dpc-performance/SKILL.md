---
name: migration-dpc-performance
description: DPC architecture dispatch tax, component execution overhead, and optimisation strategies for METL to DPC migration. Covers the systemic performance gap, IF component slowness, CIS message limits, and data sampling timeouts.
---

# Migration DPC Performance Considerations

## When to Use
- When migrating any pipeline from METL to DPC
- When customers report pipelines running significantly slower on DPC than METL
- When sequential orchestration pipelines with many components show 5-15x slowdowns
- When customers consider reverting to METL due to performance
- When designing new DPC pipelines for optimal performance

## Why This Matters
This is the **#1 cross-cutting issue** for METL→DPC migrations. DPC has a fundamentally different execution architecture that introduces per-component overhead not present in METL. Every migration conversation should set expectations about this upfront. This is a **known product issue under active investigation** — not a misconfiguration.

> ⚠️ **Critical:** Do NOT dismiss this as misconfiguration. Do NOT tell customers to permanently redesign their pipelines. Position any workarounds as temporary while the product team addresses the root cause.

---

## The Architecture Dispatch Tax

### Root Cause
In METL, component execution is an in-process call. In DPC, the Workflow Service submits tasks via the agent gateway to the agent, then receives the response back. This round-trip introduces overhead on **every single component execution**.

### Measured Impact

| Overhead Type | Per Occurrence | Notes |
|---------------|---------------|-------|
| **Component dispatch** | ~3–15 seconds | Round-trip latency per component |
| **Strand/loop boundaries** | ~20–40 seconds | Higher overhead at parallelism boundaries |
| **IF component** | 0s (METL) → 6–9s (DPC) | Per evaluation — accumulates in branchy orchestrations |
| **Simple Python scripts** | 0.1s (METL) → 5–20s (DPC) | Component execution overhead, not script runtime |

### Impact on Real Pipelines
A pipeline with 50 sequential components can be **10–15 minutes slower** than METL by design. The overhead is:
- **~77% dispatch latency** — agent sitting idle between tasks
- **~22% component execution overhead** — genuine slowdown in individual components

---

## CIS Kafka Message Size Limit

**Severity: 🟠 High**

Large transformation SQL queries that generate very large intermediate result sets can hit the **CIS (Component Interaction Service) Kafka message size limit**. This manifests as:
- Silent pipeline failures
- Incomplete data in downstream components
- "Unknown error" messages with no clear root cause

### Remediation
- Break large transformation SQL into stages
- Materialise intermediate results to Snowflake staging tables rather than passing through the component graph
- This also relates to the grid variable payload size limit (see migration-python skill)

---

## Data Sampling Timeout (2-Minute Hard Limit)

**Severity: 🟠 High**

Data sampling in DPC Designer has a **2-minute hard timeout**. Repeated sampling without reducing row count **stacks background tasks** on the agent, causing:
- OOM events
- CPU spikes
- Apparent "unresponsive Designer" behaviour
- Pipeline failures due to resource exhaustion

### Remediation
- Always reduce sample row count before sampling large datasets
- Avoid repeated sampling on the same component — it queues multiple tasks
- For large tables, add a WHERE clause or LIMIT predicate before sampling

---

## Optimisation Strategies (Available Today)

These are **temporary workarounds** while the product team addresses the root cause:

| # | Strategy | Addresses | Impact |
|---|----------|-----------|--------|
| 1 | **Maximise parallelism** — use parallel strands where pipeline logic permits | Dispatch overhead | Reduces wall-clock time via concurrency |
| 2 | **Reduce component count** — consolidate sequential SQL into single components | Dispatch overhead | Fewer round-trips |
| 3 | **Push computation to Snowflake** — use SQL transformations and Python Pushdown | Component execution overhead | Offloads work from agent |
| 4 | **Avoid deeply nested loops/iterators** — each iteration multiplies overhead | Dispatch overhead | Linear reduction in accumulated tax |
| 5 | **Co-locate agent with data sources** — cross-region latency compounds dispatch | Dispatch overhead | Reduces per-component round-trip |
| 6 | **Size agent correctly** — memory for Python, disk for logs, CPU for concurrent pipelines | OOM / Disk exhaustion | Prevents agent crashes |
| 7 | **Pin production agents to "Stable" track** — avoid auto-update breakage | Agent stability | Prevents unexpected regressions |

---

## Detection Logic

Flag when any of the following are true:
- The pipeline has **>20 sequential components** in the longest path
- The pipeline contains **deeply nested iterators** (2+ levels)
- The pipeline contains **many IF branches** in sequence
- The pipeline ran significantly faster on METL (customer-reported)
- Large transformation SQL generates very large intermediate results
- Agent OOM or timeout events appear in logs

## Priority Summary

| Category | Severity | Priority |
|----------|----------|----------|
| Architecture dispatch tax | 🔴 Critical | Set expectations pre-migration; apply optimisation strategies |
| IF component overhead (6–9s per eval) | 🔴 Critical | Consolidate conditional logic where possible |
| CIS Kafka message size limit | 🟠 High | Materialise intermediate results to staging tables |
| Data sampling timeout stacking | 🟠 High | Reduce sample row count; avoid repeated sampling |