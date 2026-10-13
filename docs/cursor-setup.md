# Using the prompts with Cursor

The prompts are reusable instructions, not exported Cursor settings. Configure an automation in your own account using [Cursor Automations](https://cursor.com/docs/cloud-agent/automations).

## Start with a bounded task

Use a repository and test environment you are authorised to access. Choose one task with acceptance criteria and an accountable human owner. Keep private data out of the prompt and provide only the context necessary for that task.

Start with a manually initiated run while you validate the workflow. A schedule or webhook can be configured later. This repository does not include a live trigger, account credentials, enabled integration or production deployment.

## Configure the implementation role

Use [implementation.md](../prompts/implementation.md) as the instructions. Replace its example context with the approved task and repository commands. Restrict tools and credentials to the scope of that task. Require an implementation report recording the resulting commit SHA and commands executed.

Do not enable automatic release based on the prompt. Cursor tools and service permissions must enforce the access boundary outside the agent's instructions.

## Run independent reviews

Use [independent-review.md](../prompts/independent-review.md) in separate review contexts. Assign one role per reviewer: backend, frontend, PR-readiness or technical QA. Supply the task, the exact commit and relevant evidence. Reviewers must inspect the implementation independently and must not inherit the implementer's conclusion as their verdict.

The four roles are appropriate for this example contract. Adapt them to the actual change; do not ask a reviewer to invent frontend or backend evidence for a task that has no such scope. This demo's fixed policy expects all four roles, so changing the role set also requires changing the gate and its tests.

## Assemble and validate evidence

The JSON examples document the expected report shape. In an operational setup, collect the current commit and CI results from trusted systems and validate reviewer provenance. Do not ask the implementation agent to fabricate passing review or CI records.

Run `python3 demo.py --evidence path/to/synthetic-report.json` to inspect an educational report. The gate intentionally accepts only reports labelled `synthetic: true`; connecting real evidence requires a separate, reviewed integration.

On FAIL, use [remediation.md](../prompts/remediation.md), then rerun independent checks on the new commit. Stop after two unresolved correction cycles or whenever the evidence is missing, stale or inconclusive. On PASS, send the evidence to the accountable human through your approved process.

## Export versus this reconstruction

Cursor's [official Terraform provider](https://github.com/cursor/terraform-provider-cursor) can read an existing automation by ID or import it into Terraform. This repository contains no exported account configuration, Terraform state, integration identifiers or private webhook endpoints. Its public prompts and fixtures are a reconstruction of the workflow pattern.
