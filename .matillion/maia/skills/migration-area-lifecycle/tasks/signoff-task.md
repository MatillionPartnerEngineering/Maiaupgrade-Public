<!-- Task template for the migration-area-lifecycle skill, phase: sign-off.
     FDE-driven gate — NOT a Maia ACT task. Placeholders {AREA} {N} {M}
     {PIPELINE_LIST} are filled per area by `fde-toolkit gen-eval`. -->

# sign-off — {AREA}

## Intent
Sign off area '{AREA}'. Confirm the imported pipelines have been validated (G1 green), tested
(ACT outputs match the METL baseline — G2/G3/G4 green), and any optimisation work held
parity. FDE-driven — this is a gate, not a Maia task. Check the audit trail of the upstream
tasks before approving.

## Applicable Maia skills
- migration-area-lifecycle (phase: sign-off)
- migration-validation

## Gate
Reads the upstream verdicts; executes nothing. Approve only when: all {N} pipelines are
validate-G1-green; test verdicts are all-gates-green (drifts triaged/accepted or remediated);
optimise (if run) held parity. Record the decision and rationale.

## Customer inventory
Imported pipelines ({N}):
{PIPELINE_LIST}

Unmatched expected jobs ({M}): tracked as customer-side publish work; do not block sign-off
of imported pipelines unless a gap breaks a tested dependency.
