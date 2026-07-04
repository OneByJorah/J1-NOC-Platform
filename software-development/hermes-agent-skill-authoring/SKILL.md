---
name: hermes-agent-skill-authoring
description: "Author valid Hermes SKILL.md files, both in-repo and user-local. Covers frontmatter rules, validator constraints, peer-matched structure and directory placement. Also covers review-receipt and update-release checklist formats for inbound PR reviews."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [plan, requesting-code-review]
---

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `skills/<category>/<name>/SKILL.md` in the hermes-agent repo — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `skills/` (use `patch` for small edits, `write_file` for rewrites)

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:
- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by most skills in the repo:
```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` are NOT enforced by the validator, but every peer has them.

## Size Limits
- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Aim for **8-14k chars**. If pushing past 20k, split into `references/*.md` and reference them.

## Peer-Matched Structure
- `# <Title>`
- `## Overview` — what and why
- `## When to Use` — triggers and counter-triggers
- `## <Topic sections>` — code blocks, quick-reference tables, Hermes-specific recipes
- `## Common Pitfalls` — mistakes and fixes
- `## Verification Checklist` — checkbox list

## Directory Placement
```
skills/<category>/<skill-name>/SKILL.md
```

Pick the closest existing category from `ls skills/`:
`agent-skills`, `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `github`, `hermes-tts`, `media`, `mlops`, `note-taking`, `ntp-dashboard`, `ntp-dashboard-prd`, `productivity`, `red-teaming`, `research`, `self-hosted-hermes-tools`, `smart-home`, `social-media`, `software-development`, `yuanbao`.

## Workflow
1. Survey peers in the target category (`ls skills/<category>/`). Read 2-3 peers.
2. Draft.
3. `write_file` the SKILL.md.
4. Git add + commit on the active branch.
5. Note: the CURRENT session's skill loader is cached. New skills won't appear until a new session.

## Cross-Referencing Other Skills
`metadata.hermes.related_skills` unifies the in-repo tree and the user-local tree at load time. Prefer referencing only in-repo skills from in-repo skills.

## Editing Existing In-Repo Skills
- Small fix: `skill_manage(action='patch')` works on in-repo skills.
- Major rewrite: `write_file` the whole SKILL.md.
- Supporting files: `write_file` to `skills/<category>/<name>/references/<file>.md`, `templates/<file>`, or `scripts/<file>`.
- Always commit the edit.

## Common Pitfalls
1. Using `skill_manage(action='create')` for an in-repo skill — it writes to `~/.hermes/skills/`, not the repo tree.
2. Leading whitespace before `---` — the validator checks `content.startswith("---")`.
3. Description too generic — "Use when debugging X" > "Debug X".
4. Forgetting author/license/metadata — every peer has it.
5. Mirror-duplicating an existing SKILL — prefer extending an existing skill.
6. Expecting the current session to see the new skill — it won't until next session.
7. Linking to user-local-only skills from in-repo skills — breaks for other clones.

## Review-Receipt Format
Use when the user asks to "reply to the review", "publish an `r=...` receipt", "set severity", or "reply to reviewer ".

### Canonical receipt
```
<role> reply to reviewer <reviewer>
<severity> <r:ID, severity=...>
<status> severity=...
<rationale> rationale
<response> response
<advice> advice
<owner> <owner>
<changes_requested_count> N
<action> reply
```

Fields
- `reviewer` — reviewer handle / login.
- `severity` — `NONE` / `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`.
- `rationale` — summary of severity and owner acknowledgement.
- `response` — short response text.
- `advice` — guidance for the author / assignee.
- `owner` — team/handle that will action the requested changes.
- `changes_requested_count` — integer count of changes requested, including comment-only items if treated as action items.

See `references/review-receipt-format.md` for examples and multi-reviewer variants.

## Update-Release Checklist
Use when the user asks to "reconcile REVIEW edits", "review for merge", "do a release checklist", or "release+".

### Branch rule
- Reconcile review edits on the integration branch before returning to `main`.
- Do not hold review changes on a feature branch unless there is already another upstream merge pass coming.
- Prefer the simpler path: land edit-first, then re-probe.

### Review-state contract
- Treat each reviewer's latest review-event as the source of truth.
- A single `APPROVED` event earlier does not override a later `CHANGES_REQUESTED`.
- Only after a reviewer approval event with no pending `CHANGES_REQUESTED` can the state be treated as accepted with respect to that reviewer.

### Commit-order risk
- Apply fix commits first.
- Then finalize merge / release.
- Do not merge in a way that buries `CHANGES_REQUESTED` between fix commits and the merge commit.

### Dashboard / nginx validation
Always validate the live landing surface before reviewing for merge:
1. `curl -s http://127.0.0.1:8080/healthz`
2. `curl -s http://127.0.0.1:8080/`
3. Verify port in use: `ss -ltnp | grep ':8080'`
4. If `nginx.conf` was touched, run `nginx -t` and report bindings / socket state.
5. Inspect in browser when the candidate involves UI changes.

Never accept only HTTP 200 as proof. Confirm the served body actually represents the intended dashboard revision.

### GitHub housekeeping
- Close no-longer-needed PRs explicitly (`gh pr close <n> --reason "not planned"`).
- A "closed" state is not the same as "merged"; keep the taxonomy correct.
- Toggles or blind merges are not a substitute for review-state contracts.

### Public repo exposure guard
- Public repo docs must not include internal access notes that expose private infrastructure.
- Do not publish raw IPs (`<tailnet-cidr>`, `192.168.x.x`), internal hostnames, or credential strings in README / converted markdown.
- Before converting docs for public commit, sweep access notes with a search pass.

### Durable pruning signals
A narrow, immediately-actionable item is durably actionable when it meets both:
1. Low friction to repeat — can be done in one local terminal command.
2. Low cost to trust — correctness is self-evident from the direct output.

Otherwise, raise the issue as a finding or move it under documentation/reference tracking.

## Partner Skills

This guide complements (does not absorb) the GitHub shortcut skills:
- `github` — broad GitHub workflow is now handled by the `github` umbrella.