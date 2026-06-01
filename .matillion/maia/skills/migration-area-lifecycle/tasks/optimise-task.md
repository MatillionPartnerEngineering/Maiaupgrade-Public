<!-- Task template for the migration-area-lifecycle skill, phase: optimise.
     Placeholders {AREA} {N} {PIPELINE_LIST} are filled per area by
     `fde-toolkit gen-eval`. -->

# optimise-task — {AREA}

## Intent
Optimise the {N} imported pipelines in area '{AREA}'. Improve a target metric (runtime,
compute, or component count) WITHOUT changing behaviour — the four-gate verdict must remain
green and content parity (G3/G4) must hold against the METL baseline.

## Applicable Maia skills
- migration-area-lifecycle (phase: optimise)

## Gates
G1 → G4 must stay green after each change. Reject any optimisation that alters output
(parity break). Introduce no new deprecated components. Report the metric delta with a
parity-held confirmation.

## Customer inventory
Imported pipelines ({N}):
{PIPELINE_LIST}
