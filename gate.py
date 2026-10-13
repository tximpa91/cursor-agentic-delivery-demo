"""Validate synthetic delivery evidence. No network, subprocesses or write actions."""

from dataclasses import asdict, dataclass
import re

REVIEW_ROLES = ("backend", "frontend", "pr_readiness", "technical_qa")
CHECK_NAMES = ("build", "unit", "lint")
MAX_REMEDIATION_CYCLES = 2
SHA = re.compile(r"[0-9a-f]{40}", re.ASCII)


@dataclass(frozen=True)
class Decision:
    verdict: str
    next_action: str
    reasons: tuple[str, ...]
    commit_sha: str | None = None

    def to_dict(self):
        return asdict(self)


def stop(reason, commit=None):
    return Decision("ESCALATE", "STOP", (reason,), commit)


def evaluate(evidence):
    """Fail closed on absent, malformed, stale or contradictory evidence."""
    if not isinstance(evidence, dict):
        return stop("Evidence must be a JSON object.")
    if evidence.get("schema_version") != "1.0" or evidence.get("synthetic") is not True:
        return stop("This demo accepts only version 1.0 synthetic evidence.")
    if not isinstance(evidence.get("run_id"), str) or not evidence["run_id"].strip():
        return stop("A non-empty run_id is required.")
    commit = evidence.get("head_sha")
    if not isinstance(commit, str) or SHA.fullmatch(commit) is None:
        return stop("head_sha must be a lowercase 40-character hexadecimal commit SHA.")
    cycles = evidence.get("remediation_cycles")
    if type(cycles) is not int or cycles < 0:
        return stop("remediation_cycles must be a non-negative integer.", commit)
    if cycles > MAX_REMEDIATION_CYCLES:
        return stop("The two-cycle remediation limit has been exceeded.", commit)
    task = evidence.get("task")
    if not isinstance(task, dict) or task.get("human_scope_approved") is not True:
        return stop("Human approval of task scope is missing.", commit)
    if task.get("risk") != "low":
        return stop("This example policy only permits low-risk tasks.", commit)
    if task.get("requested_action") != "prepare_change":
        return stop("This example policy permits preparing changes only.", commit)
    implementation = evidence.get("implementation")
    if not isinstance(implementation, dict):
        return stop("Implementation evidence is missing.", commit)
    implementer = implementation.get("agent_id")
    if not isinstance(implementer, str) or not implementer.strip():
        return stop("Implementation agent identity is missing.", commit)
    if implementation.get("commit_sha") != commit:
        return stop("Implementation evidence does not match the current commit.", commit)
    reviews = evidence.get("reviews")
    if not isinstance(reviews, list) or len(reviews) != len(REVIEW_ROLES):
        return stop("Exactly four independent role reviews are required.", commit)
    seen_roles, reviewer_ids, problems = set(), set(), []
    for review in reviews:
        if not isinstance(review, dict):
            return stop("Every review must be an object.", commit)
        role = review.get("role")
        if not isinstance(role, str) or role not in REVIEW_ROLES or role in seen_roles:
            return stop("Review roles must be supported and unique.", commit)
        seen_roles.add(role)
        reviewer = review.get("agent_id")
        if not isinstance(reviewer, str) or not reviewer.strip():
            return stop("Reviewer identity is missing.", commit)
        if reviewer == implementer or reviewer in reviewer_ids:
            return stop("Implementation and review identities must be independent.", commit)
        reviewer_ids.add(reviewer)
        if review.get("commit_sha") != commit:
            return stop(f"{role} review does not match the current commit.", commit)
        verdict, findings = review.get("verdict"), review.get("findings")
        if not isinstance(verdict, str) or verdict not in ("PASS", "FAIL", "ESCALATE"):
            return stop(f"{role} review has no supported verdict.", commit)
        if not isinstance(findings, list) or any(not isinstance(f, str) or not f.strip() for f in findings):
            return stop(f"{role} findings must be a list of non-empty strings.", commit)
        if verdict == "ESCALATE":
            return stop(f"{role} reviewer requires human attention.", commit)
        if verdict == "PASS" and findings:
            return stop(f"{role} PASS contradicts its unresolved findings.", commit)
        if verdict == "FAIL":
            if not findings:
                return stop(f"{role} FAIL lacks actionable findings.", commit)
            problems.extend(f"{role}: {f}" for f in findings)
    checks = evidence.get("ci_checks")
    if not isinstance(checks, list) or len(checks) != len(CHECK_NAMES):
        return stop("Build, unit and lint evidence are all required.", commit)
    seen_checks = set()
    for check in checks:
        if not isinstance(check, dict):
            return stop("Every CI check must be an object.", commit)
        name = check.get("name")
        if not isinstance(name, str) or name not in CHECK_NAMES or name in seen_checks:
            return stop("CI check names must be supported and unique.", commit)
        seen_checks.add(name)
        if check.get("commit_sha") != commit:
            return stop(f"{name} CI evidence does not match the current commit.", commit)
        result = check.get("result")
        if not isinstance(result, str) or result not in ("success", "failure"):
            return stop(f"{name} CI has not returned a conclusive result.", commit)
        if result == "failure":
            problems.append(f"CI check failed: {name}.")
    if problems:
        if cycles >= MAX_REMEDIATION_CYCLES:
            return Decision("ESCALATE", "STOP", tuple(problems) + ("Two remediation cycles ended without valid passing evidence.",), commit)
        return Decision("FAIL", "REMEDIATE", tuple(problems), commit)
    return Decision("PASS", "HUMAN_REVIEW", ("All required reviews and CI checks match the current commit.",), commit)
