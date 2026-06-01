<!-- Task template for the migration-area-lifecycle skill, phase: test.
     Placeholders {AREA} {N} {M} {PIPELINE_LIST} are filled per area by
     `fde-toolkit gen-eval`. -->

# test-task — {AREA}

## Intent
Test {N} imported pipelines in area '{AREA}'. Execute each pipeline in ACT mode against the
test environment. For every pipeline, apply the four-gate verdict (G1→G4) against the METL
baseline and surface failures as gate-tagged events. {M} expected job(s) have no matching
pipeline — tests run on what is imported, gaps are flagged on the task event log.

## Applicable Maia skills
- migration-area-lifecycle (phase: test) — owns the four-gate verdict
- migration-test-execution — entry-point-first ordering, failure classification

## Gates
G1 → G2 → G3 → G4 (escalating ladder, short-circuit on first failure). Compare G3/G4 against
the committed baseline (`baseline.json`). Emit `gate:Gn` events; assign each pipeline a
verdict (PASS / PARITY_DRIFT / VOLUME_DRIFT / FAILED_EXECUTION / BLOCKED_COMPILE).

## Customer inventory
Imported pipelines ({N}):
{PIPELINE_LIST}

Unmatched expected jobs ({M}): flagged as gaps.
