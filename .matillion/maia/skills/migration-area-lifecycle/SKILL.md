---
name: migration-area-lifecycle
description: Use when driving an imported area through the migration lifecycle — validate (PLAN), test (ACT + four-gate verdict), optimise, and sign-off — against the METL baseline.
schema_version: 1
phases:
  - validation
  - execution
detection_rules:
  - id: unmatched-expected-job
    title: Expected job with no matching imported pipeline
    reference: "migration_documentation.md → Upgrade: scope & coverage"
    body_anchor: unmatched-expected-job
    severity: advisory
    applies_when:
      signals: [expected-job-no-pipeline]
---

# Migration Area Lifecycle

## When to Use
- Driving a functional area of imported pipelines through to sign-off.
- Whenever the FDE issues a `validate`, `test`, `optimise`, or `sign-off` task for an area.
- As the orchestrator that sequences and delegates to `migration-validation` (PLAN
  detection) and `migration-test-execution` (ACT methodology).

## Why This Matters
Imported pipelines are not "migrated" until they have been proven to behave the same as
METL. This skill defines the single lifecycle every area passes through and the **four-gate
verdict** that decides whether a pipeline has actually preserved behaviour. The verdict is
defined once, here, and is the contract the FDE eval suite scores against — the agent and
the eval must agree on what "passed" means.

## The lifecycle

```
validate (PLAN) ──▶ test (ACT) ──▶ optimise (ACT) ──▶ sign-off (FDE gate)
  Gate G1 only      Gates G1→G4     parity must hold     reads the audit trail
```

| Phase | Mode | Gates | Boundary |
|-------|------|-------|----------|
| **validate** | PLAN | G1 only | **No write may be attempted.** Confirms compile + clean plan. |
| **test** | ACT | G1 → G4 | Executes against the test environment; full verdict per pipeline. |
| **optimise** | ACT | G1 → G4 must stay green | Improve a metric **without** changing behaviour; parity must hold. |
| **sign-off** | — | reads verdicts | FDE-driven gate, **not** a Maia task. Checks the upstream audit trail. |

The lifecycle is applied **per area**; the verdict is applied **per imported pipeline**.

---

## The four-gate verdict

An **escalating ladder**: each gate presupposes the one below passed. A failure at gate _N_
**short-circuits** gates _N+1…4_ — the verdict is the gate the pipeline stopped at, and the
higher gates are reported `not_reached` (never `pass`). Emit every gate outcome as a
`gate:Gn` event on the task event log.

<a id="gate-g1"></a>
### Gate G1 — Compile & Plan  (severity: blocker)
Pipeline compiles; all component configs resolve; referenced connections, secrets, and
shared pipelines exist and are reachable; the execution plan resolves end-to-end; **no write
is attempted**. This is the only gate the `validate` task evaluates (PLAN mode). The `test`
task re-confirms it in the live ACT environment first.
- Pass: compiles AND plan clean AND zero writes attempted.
- Fail → verdict `BLOCKED_COMPILE`. Event `gate:G1`.

<a id="gate-g2"></a>
### Gate G2 — Execute  (severity: blocker)
Pipeline runs to completion in ACT with no component error, agent crash, OOM, or timeout;
all declared outputs are produced.
- Pass: run completes, zero errored steps, outputs present.
- Fail → verdict `FAILED_EXECUTION`. Event `gate:G2`.

<a id="gate-g3"></a>
### Gate G3 — Volume & Shape  (severity: warning)
For each output, the column set + types match the METL baseline schema (always exact), and
the row count matches the baseline within the pipeline's declared `volumeTolerancePct`
(default exact).
- Fail → verdict `VOLUME_DRIFT`. Event `gate:G3`.

<a id="gate-g4"></a>
### Gate G4 — Content Parity  (severity: warning)
Output content matches the METL baseline: by content hash where deterministic, else by
sorted sampled-row comparison. Columns the migration legitimately regenerates (load
timestamps, regenerated surrogate keys, audit columns) are excluded via an **explicit,
reviewed** `parityIgnoreColumns` list — never a blanket tolerance.
- Fail → verdict `PARITY_DRIFT`. Event `gate:G4`.

### Verdict roll-up
A pipeline's verdict is the **highest gate it reached**:

| Verdict | G1 | G2 | G3 | G4 |
|---------|----|----|----|----|
| `PASS` | ✓ | ✓ | ✓ | ✓ |
| `PARITY_DRIFT` | ✓ | ✓ | ✓ | ✗ |
| `VOLUME_DRIFT` | ✓ | ✓ | ✗ | — |
| `FAILED_EXECUTION` | ✓ | ✗ | — | — |
| `BLOCKED_COMPILE` | ✗ | — | — | — |

`not_reached` (—) is never reported as `pass`.

---

<a id="unmatched-expected-job"></a>
## Unmatched expected jobs are gaps, not failures

An expected job with **no matching imported pipeline** is **not** a gate failure and must not
drag an area's verdict down. Surface it as a distinct event:
- Event tag: `gap:unmatched-expected-job`
- Classification: customer-side work to publish, recorded on the task event log.

Gates apply only to pipelines that were actually imported. This rule is identical in the
`validate` and `test` tasks.

---

## How to run each phase

### validate (PLAN)
1. For each imported pipeline, run once in PLAN mode. Evaluate **G1 only**. Attempt **no
   write**.
2. Delegate component-level detection to `migration-validation` (Python, Bash, API
   Extract/Query, JDBC, etc.) — its blockers feed G1.
3. Emit `gate:G1 pass|fail` per pipeline; emit `gap:unmatched-expected-job` per unmatched
   expected job.
4. Exit when every imported pipeline has a G1 verdict.

### test (ACT)
1. Re-confirm G1 against the live test environment, then walk G2 → G4 per pipeline.
2. Use `migration-test-execution` for entry-point-first ordering (simplest → most complex)
   to avoid cascading failures.
3. Compare G3/G4 against the committed baseline (`baseline.json`). Emit `gate:Gn` events;
   short-circuit on the first failed gate.
4. Exit when every imported pipeline has a four-gate verdict.

### optimise (ACT)
1. Apply an optimisation (runtime, compute, component count). Re-run.
2. Re-evaluate G1 → G4. **Parity (G3/G4) must stay green** — an optimisation that changes
   output is rejected. Introduce no new deprecated components.
3. Report the metric delta alongside a parity-held confirmation.

### sign-off (FDE gate — not a Maia task)
1. Read the audit trail of the upstream tasks for the area.
2. Confirm: validate G1-green for all imported pipelines; test all-gates-green (drifts
   triaged/accepted or remediated); optimise (if run) held parity.
3. Approve the area only when those hold. Record the decision; do **not** execute pipelines.

---

## Task templates
Per-area task instances for this skill are generated by the FDE toolkit
(`fde-toolkit gen-eval --area <name>`) and live alongside this skill as
`tasks/{validate,test,optimise,signoff}-task.md`. They are the agent-facing entry points;
this SKILL.md is the behaviour they invoke.

## Key Lessons
1. **The verdict lives in one place.** If the eval suite and this skill disagree on a gate,
   this file wins — update both together.
2. **PLAN never writes.** A `validate` task that writes has failed its own contract,
   regardless of pipeline behaviour.
3. **Gaps ≠ failures.** Unmatched expected jobs are customer-side publish work; scoring them
   as failures hides real regressions behind noise.
4. **Short-circuit honestly.** Never green a higher gate a pipeline never reached.
