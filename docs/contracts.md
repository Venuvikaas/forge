# Data Contracts (FROZEN — change only by mutual agreement + a commit)

This is the seam between the two lanes. **Dev B builds the App against these shapes using mock/seed
data while Dev A builds the real pod.** Neither lane renames a field without updating this file and
telling the other person.

---

## 1. `issues` Table

| Field | Type | Notes |
|---|---|---|
| `id` | string (PK) | Forge-internal id, e.g. `iss_001` |
| `source` | enum | `github` \| `slack` \| `email` |
| `external_id` | string | e.g. GitHub issue number `#142`; null for seeded chat |
| `title` | string | short summary |
| `body` | text | full report text (also written to Files) |
| `priority` | enum \| null | `critical` \| `high` \| `normal` \| `low`; null until triaged |
| `repro_steps` | text (markdown) \| null | bullet list; null until triaged |
| `status` | enum | `new` \| `triaged` \| `investigating` \| `resolved` |
| `related_ids` | string[] | ids of confirmed duplicates / related issues |
| `linked_prs` | string[] | PR identifiers that fix it (optional) |
| `created_at` | ISO datetime | |
| `updated_at` | ISO datetime | |

## 2. Files convention (powers dedup + RAG)

- One file per issue: path `/issues/{id}.md`, content = `# {title}\n\n{body}`.
- Product docs (optional) under `/knowledge/...`.
- Search: `pod.files.search(query, scope_path="/issues", search_method="HYBRID")`.

## 3. Triage agent — output JSON (strict)

```json
{
  "priority": "critical | high | normal | low",
  "repro_steps": "- step one\n- step two",
  "reason": "one short sentence — evidence-based, NO fabricated percentages"
}
```
`normalize_priority` Function validates this → coerces unknown/missing priority to `normal`.

## 4. Duplicate confirmation — agent output

```json
{ "is_duplicate": true, "reason": "same null-pointer in auth/cache.py" }
```

## 5. Investigation Workflow — result shape

```json
{
  "issue_id": "iss_001",
  "hypothesis": "One paragraph: most likely root cause and where.",
  "evidence": [
    { "type": "commit | issue | log | file", "label": "human-readable", "url": "https://..." }
  ]
}
```
UI rule: render evidence as clickable links. **No confidence %** — show evidence, not vibes.

## 6. Release notes (only if Release Center is GO) — result shape

```json
{
  "version": "1.2.0",
  "groups": { "Added": ["..."], "Fixed": ["..."], "Changed": ["..."] },
  "markdown": "## 1.2.0\n\n### Added\n- ..."
}
```

---

### Change log for this contract
- 2026-06-25 — initial freeze (Phase 0).
