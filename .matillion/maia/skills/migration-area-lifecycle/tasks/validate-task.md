<!-- Task template for the migration-area-lifecycle skill, phase: validate.
     Placeholders {AREA} {N} {M} {PIPELINE_LIST} are filled per area by
     `fde-toolkit gen-eval`. -->

# validate-task — {AREA}

## Intent
Validate {N} imported pipelines in area '{AREA}'. Run each pipeline once in PLAN mode,
confirm it compiles and the agent reports a clean execution path (Gate G1). Do not execute
writes yet — that is the test task. {M} expected job(s) have no matching pipeline yet —
surface them as customer-side work to publish rather than failing the validation.

## Applicable Maia skills
- migration-area-lifecycle (phase: validate) — owns Gate G1 and the gap rule
- migration-validation — component-level blocker detection feeding G1

## Gate
G1 (Compile & Plan) only. No write may be attempted. Emit `gate:G1 pass|fail` per pipeline
and `gap:unmatched-expected-job` per unmatched expected job.

## Customer inventory
Imported pipelines ({N}):
{PIPELINE_LIST}

Unmatched expected jobs ({M}): surfaced as gaps, not failures.
