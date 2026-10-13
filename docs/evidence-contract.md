# Example evidence contract

All included records are synthetic. The all-`a` and all-`b` commit hashes identify fictional versions for the demonstration, and the agent IDs are illustrative labels.

## Required report fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Exactly `1.0` for this public demo |
| `synthetic` | Exactly `true`; this gate does not accept operational reports |
| `run_id` | Non-empty report identifier |
| `head_sha` | Current lowercase 40-character hexadecimal commit SHA |
| `remediation_cycles` | Completed correction cycles, an integer from 0 through 2 |
| `task.human_scope_approved` | Explicit approval of the bounded task scope |
| `task.risk` | `low` under this example policy |
| `task.requested_action` | `prepare_change`; release actions are out of scope |
| `implementation` | Implementation agent ID and matching commit SHA |
| `reviews` | Exactly one backend, frontend, PR-readiness and technical-QA review |
| `ci_checks` | Exactly one build, unit-test and lint record |

Each review must include its role, agent ID, matching commit SHA, verdict and a list of unresolved findings. Reviewer IDs must be unique and must differ from the implementer. PASS must have no unresolved findings; FAIL must have at least one actionable finding; ESCALATE stops the run.

Each CI record must identify a required check name, the matching commit SHA and a conclusive `success` or `failure` result. Pending, missing and stale checks do not count as passing evidence.

## Decisions

The gate first checks policy and evidence integrity. Missing scope approval, unsupported actions, absent records, identity conflicts, stale commits and contradictory verdicts produce ESCALATE/STOP. If evidence is structurally complete but contains a negative review or failed check, it produces FAIL/REMEDIATE while fewer than two correction cycles have completed. At two unresolved cycles it produces ESCALATE/STOP. Matching positive evidence produces PASS/HUMAN_REVIEW, including after a successful second correction cycle.

Extra descriptive fields such as a task summary or evidence note are not trusted as a verdict. JSON files with duplicate keys are rejected by the CLI loader.

## Limits

The contract checks supplied values. A matching SHA string is not proof of code provenance; a distinct reviewer label is not proof of an isolated review; a successful check label is not proof of a CI run. A production integration must obtain and bind those records from trusted systems. Synthetic snapshots demonstrate the decision rules without claiming that such an integration is running in this repository.
