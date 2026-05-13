#!/usr/bin/env python3
"""Schema linter for `.matillion/maia/skills/<id>/SKILL.md`.

Validates every SKILL.md in the repo against the v1 contract documented
in `.matillion/maia/SCHEMA.md`. Fails the run when a v1 skill (one that
declares `schema_version: 1`) is broken — missing body anchors, invalid
severity values, unknown phases, duplicate rule ids, etc. v0 skills
(no `schema_version`) are tolerated so the catalog can mix legacy
prose-only skills with promoted structured ones.

Designed to be runnable both locally (`python scripts/lint_skills.py`)
and in GitHub Actions (zero deps beyond pyyaml, which CI installs).

Exit codes:
    0  every v1 skill is clean (v0 skills tolerated).
    1  at least one v1 skill has integrity errors.
    2  the script itself failed (e.g. missing pyyaml).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs this; only here for local
    print("error: pyyaml not installed. Run `pip install pyyaml`.", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / ".matillion" / "maia" / "skills"

VALID_SEVERITIES = frozenset({"blocker", "warning", "advisory"})
VALID_PHASES = frozenset({"discovery", "refactor", "validation", "execution"})

ANCHOR_RE = re.compile(r'<a\s+id="([^"]+)"\s*></a>')


@dataclass(frozen=True)
class Issue:
    skill: str
    rule: str | None
    severity: str  # "error" | "warning"
    message: str


def main() -> int:
    if not SKILLS_ROOT.is_dir():
        print(f"error: skills root not found at {SKILLS_ROOT}", file=sys.stderr)
        return 2

    issues: list[Issue] = []
    v1_count = 0
    v0_count = 0

    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        try:
            frontmatter, body = _split_frontmatter(skill_md)
        except ValueError as e:
            issues.append(Issue(skill_dir.name, None, "error", str(e)))
            continue

        if frontmatter is None:
            # No frontmatter at all — uncommon but not strictly a v1 violation.
            issues.append(
                Issue(skill_dir.name, None, "warning", "missing YAML frontmatter")
            )
            continue

        schema_version = int(frontmatter.get("schema_version") or 0)
        if schema_version < 1:
            v0_count += 1
            continue

        v1_count += 1
        issues.extend(_lint_v1_skill(skill_dir.name, frontmatter, body))

    return _report(issues, v1_count, v0_count)


def _lint_v1_skill(skill_name: str, frontmatter: dict, body: str) -> list[Issue]:
    issues: list[Issue] = []

    name = frontmatter.get("name", "")
    if name and name != skill_name:
        issues.append(
            Issue(
                skill_name,
                None,
                "error",
                f"frontmatter name '{name}' does not match directory '{skill_name}'",
            )
        )

    phases = frontmatter.get("phases") or []
    if not isinstance(phases, list):
        issues.append(Issue(skill_name, None, "error", "phases must be a list"))
    else:
        for phase in phases:
            if phase not in VALID_PHASES:
                issues.append(
                    Issue(
                        skill_name,
                        None,
                        "error",
                        f"unknown phase '{phase}' (expected one of {sorted(VALID_PHASES)})",
                    )
                )

    rules = frontmatter.get("detection_rules") or []
    if not isinstance(rules, list):
        issues.append(
            Issue(skill_name, None, "error", "detection_rules must be a list")
        )
        return issues
    if not rules:
        # v1 skill with no rules is valid (e.g. only the operating contract
        # contribution matters) — emit a warning so the author is nudged.
        issues.append(
            Issue(
                skill_name,
                None,
                "warning",
                "schema_version: 1 declared but detection_rules is empty",
            )
        )

    anchor_counts: dict[str, int] = {}
    for a in ANCHOR_RE.findall(body):
        anchor_counts[a] = anchor_counts.get(a, 0) + 1

    seen_rule_ids: set[str] = set()
    for idx, rule in enumerate(rules):
        if not isinstance(rule, dict):
            issues.append(
                Issue(
                    skill_name,
                    f"#{idx}",
                    "error",
                    f"rule entry {idx} is not a mapping",
                )
            )
            continue

        rule_id = (rule.get("id") or "").strip()
        if not rule_id:
            issues.append(
                Issue(skill_name, f"#{idx}", "error", "rule missing id")
            )
            continue

        if rule_id in seen_rule_ids:
            issues.append(
                Issue(skill_name, rule_id, "error", f"duplicate rule id '{rule_id}'")
            )
        seen_rule_ids.add(rule_id)

        anchor = (rule.get("body_anchor") or "").strip()
        if not anchor:
            issues.append(
                Issue(skill_name, rule_id, "error", "missing body_anchor")
            )
        elif anchor_counts.get(anchor, 0) == 0:
            issues.append(
                Issue(
                    skill_name,
                    rule_id,
                    "error",
                    f"body_anchor '{anchor}' not present in skill body",
                )
            )
        elif anchor_counts[anchor] > 1:
            issues.append(
                Issue(
                    skill_name,
                    rule_id,
                    "error",
                    f"body_anchor '{anchor}' appears multiple times in body",
                )
            )

        severity = (rule.get("severity") or "").strip().lower()
        if severity not in VALID_SEVERITIES:
            issues.append(
                Issue(
                    skill_name,
                    rule_id,
                    "error",
                    f"invalid severity '{severity}' (expected one of {sorted(VALID_SEVERITIES)})",
                )
            )

        applies_when = rule.get("applies_when") or {}
        if not isinstance(applies_when, dict):
            issues.append(
                Issue(
                    skill_name,
                    rule_id,
                    "error",
                    "applies_when must be a mapping",
                )
            )
            continue
        # Soft check: at least one selector key should be populated.
        has_any = any(
            isinstance(applies_when.get(k), list) and applies_when[k]
            for k in ("component_types", "project_types", "signals")
        )
        if not has_any:
            issues.append(
                Issue(
                    skill_name,
                    rule_id,
                    "warning",
                    "applies_when has no selector keys populated — rule is always-applies",
                )
            )

    return issues


def _split_frontmatter(skill_md: Path) -> tuple[dict | None, str]:
    """Return (parsed_frontmatter, body) or raise ValueError on malformed YAML.

    Returns ``(None, body)`` for files that have no frontmatter at all.
    """
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text

    end_idx: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("missing closing frontmatter delimiter")

    frontmatter_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])

    try:
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise ValueError(f"malformed YAML frontmatter: {e}") from e

    if data is None:
        return {}, body
    if not isinstance(data, dict):
        raise ValueError(
            f"frontmatter must be a mapping, got {type(data).__name__}"
        )
    return data, body


def _report(issues: list[Issue], v1_count: int, v0_count: int) -> int:
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    print(
        f"Scanned {v1_count + v0_count} skills "
        f"({v1_count} schema_version=1, {v0_count} v0)."
    )
    if not issues:
        print("✓ all skills pass lint.")
        return 0

    for issue in issues:
        loc = f"{issue.skill}" + (f"/{issue.rule}" if issue.rule else "")
        prefix = "ERROR" if issue.severity == "error" else "warn"
        print(f"  [{prefix}] {loc}: {issue.message}")

    print()
    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
