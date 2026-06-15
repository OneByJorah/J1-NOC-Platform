---
name: review-receipt-format
title: PR Review Receipt / Response Format
description: >
  Canonical shaped receipt emitted after completing a formal PR review.
  Use whenever a user asks to “reply to the review”, “publish an `r=...` receipt”,
  “set severity”, or “reply to reviewer ”.
  This is a topic reference file for `hermes-agent-skill-authoring`.
---

# PR Review Receipt / Response Format

Use this template whenever the user asks: “reply to the review”, “send a review receipt”, “reply to `r=...`”, or equivalent.

## Receipt shape
```
<role> reply to reviewer <reviewer>
<severity> <r:ID, severity=...>
<status> severity=...
<rationale> summary of severity and owner acknowledgement
<owner> <owner>
<changes_requested_count> N
<action> reply
```

## Fields
- `reviewer` — the reviewer login / handle.
- `severity` — overall rating: `NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- `status` — short human status: e.g. “all accepted and deployable”, “blocked pending C4 closure”.
- `rationale` — connects severity to changes requested + owner acknowledgement.
- `owner` — team/handle that will action the requested changes.
- `changes_requested_count` — integer count including comment-only items when they are treated as action items.
- `action` — typically `reply` for PR review replies.

## Severity recommendations
- `NONE` — approved / no blocking or suggested changes.
- `LOW` — stylistic / minor; ship remains deployable as-is.
- `MEDIUM` — changes should land before merge; no security / data-path break.
- `HIGH` — breaking or correctness issue; merge blocked.
- `CRITICAL` — security / auth / data-loss / runtime-blocking issue; immediate action required.

## Multi-reviewer variant
If multiple reviewers have pending findings, collapse findings into one severity and `changes_requested_count`. Mention reviewers by name inside `rationale` only when their severity differs.
