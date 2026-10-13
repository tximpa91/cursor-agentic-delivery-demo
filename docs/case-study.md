# Building a governed Cursor delivery workflow

I built and operationalised a repository-native engineering workflow using Cursor Cloud Agents, reusable rules and skills, controlled context, and separate implementation and review agents. Its purpose was to make an AI-generated change reviewable before it could move into the normal delivery process.

## The problem

A change can look complete while its review or test evidence refers to an earlier commit. Giving an agent access to a repository does not solve that problem. Implementation, independent checking and evidence collection need clear responsibilities and a shared definition of the version being considered.

## What I built

I organised an umbrella repository and reusable engineering context, connected relevant tooling through MCP, and created bounded implementation and independent-review roles. The workflow included backend, frontend, pull-request-readiness and technical-QA checks, exact-commit-SHA validation, CI evidence digests, notifications and a two-cycle remediation limit.

The implementation role prepared a change. Separate review roles checked it and returned evidence. The workflow associated those checks with the required commit, then either continued within the allowed process, requested correction or stopped for human attention. The coding-agent workflow remained separate from customer-facing AI product work.

## A failure that demonstrated the boundary

In an audited operational run, independent reviewers found real regressions. Remediation corrected them, but the final evidence did not match the required commit. The workflow stopped without opening a pull request.

The important outcome was the stop: finding and correcting a regression did not override the requirement for evidence tied to the code under consideration. This example does not establish a quantified productivity or quality improvement.

## What this public repository demonstrates

The prompts preserve the role boundaries and evidence contract in an employer-neutral form. The Python gate and JSON fixtures are newly created public examples. They demonstrate matching evidence, a detected regression, stale CI and exhausted remediation cycles with synthetic agent IDs and commit hashes.

The Python gate validates snapshots; it does not launch agents, authenticate the reports or release code. The private operational workflow used Cursor Cloud Agents. A separate vendor-neutral control-plane architecture was designed, but this repository does not claim that architecture was deployed.

## Why the pattern transfers to applied AI

An LLM can propose a useful action while still requiring independent checks on correctness, context and permissions. This workflow connects an AI-assisted task to explicit acceptance criteria, specialised review and a bounded next action. Those principles can be adapted to customer AI solutions, provided the evaluation and controls match the customer's domain and risk.

No legal-client deployment is implied. The engineering example supplies evidence of applied AI orchestration and judgment under failure; it complements my separate production retrieval and conversational-AI experience.

## What I would evaluate next

For a new deployment, I would establish a baseline and measure accepted changes, first-pass validation, remediation effort, escaped defects, operating cost and manual handoffs. Expansion should depend on those results and the team's review capacity. A PASS verdict from a local JSON demonstration is not evidence that an operational deployment is ready for broader autonomy.
