# Maia Framework — Schema

Defines the data contract for content under `.matillion/maia/`. Consumers (Maia, fde-remediation, future tooling) use this contract to deterministically discover, select, and apply known-known migration patterns without reading prose.

## Versioning

Every catalog file declares `schema_version: <int>` in its frontmatter. Files without this field are treated as **v0** (legacy: `name` + `description` only, body injected as prose). Consumers MUST tolerate unknown fields so v1 files remain forward-compatible.

Current version: **1**

## File layout

```
.matillion/maia/
├── SCHEMA.md                         (this file)
├── rules/
│   └── *.md                          governance instructions, loaded as operating contract
└── skills/
    └── <skill-id>/
        └── SKILL.md                  skill definition + detection rules
```

## Skill frontmatter (`SKILL.md`)

```yaml
---
name: <kebab-case-id>                 # must equal directory name
description: <one-line, ≤200 chars>   # used for skill triggering
schema_version: 1
phases:                               # migration lifecycle phases this skill is active in
  - discovery | refactor | validation | execution
detection_rules:                      # ordered list; see below
  - id: <kebab-case-id>
    ...
---
```

## Detection rule schema

```yaml
- id: <kebab-case-id>                 # stable, never reused
  title: <human-readable>             # matches existing body heading
  reference: <doc anchor>             # e.g. "migration_documentation.md → Upgrade: Python"
  body_anchor: <html anchor id>       # matches an <a id="..."></a> in the body
  severity: blocker | warning | advisory   # max severity if multiple bands documented in body
  applies_when:                       # selector — at least one key required
    component_types: [...]            # Matillion component IDs (kebab-case)
    project_types: [...]              # optional: snowflake | databricks | redshift | bigquery
    signals: [...]                    # optional: cross-cutting tokens (e.g. variable-reference)
```

### Anchors in body

Each rule's prose section MUST be preceded by an HTML anchor matching its `body_anchor`:

```markdown
<a id="python-jython"></a>
### 1️⃣ Python & Jython Components
...
```

The loader reads body content from the anchor to the next anchor (or EOF). Existing prose is preserved verbatim; only anchors are added when a rule is promoted to v1.

### ID conventions

- Kebab-case, lowercase, ASCII.
- Skill IDs match their directory name.
- Rule IDs are unique within a skill and stable across PRs — **never reused after deletion**.
- Component-type tokens follow the Matillion canonical component ID in kebab-case form.

### Severity

- `blocker` — migration cannot proceed; refactor required.
- `warning` — migration may proceed but manual verification required.
- `advisory` — informational; auto-resolved during import in most cases.

When the body documents multiple severity bands ("Blocker: X, Y; Warning: Z"), declare the **max** severity here. Body prose retains the nuance until a future schema version models bands structurally.

## Validation

Consumers SHOULD validate frontmatter on load and surface errors via tooling (e.g. `remediation_validate_skills` in fde-remediation). Required fields per `schema_version: 1`:

- Skill: `name`, `description`, `schema_version`, `phases`, `detection_rules`
- Rule: `id`, `title`, `reference`, `body_anchor`, `severity`, `applies_when` (at least one selector key)

Anchor integrity: every `body_anchor` value MUST correspond to exactly one `<a id="...">` in the body.

## Migration path

- **v0 skills** (frontmatter with `name` + `description` only) remain valid; consumers fall back to body-prose injection.
- **v1 skills** declare `schema_version: 1` and a structured `detection_rules` list. Rules within a v1 skill that have not yet been promoted to structured form remain documented in the body and are exposed to consumers as v0-style prose context until promoted.
- Promotion of a rule is purely additive: append the structured entry to `detection_rules`, add an HTML anchor before the existing heading. No body content is rewritten.
