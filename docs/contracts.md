# Data Contracts (FROZEN — change only by mutual agreement + a commit)

This is the seam between the two lanes. **Dev B builds the App against these shapes using mock/seed
data while Dev A builds the real pod.** Neither lane renames a field without updating this file and
telling the other person.

---

## 1. `issues` Table

| Field | Type | Notes |
|---|---|---|
| `id` | string (PK) | Forge-internal id. **Live scheme:** github → `gh_<number>` (e.g. `gh_142`); seeded chat → `iss_001`. This is the key Dev B's App references and that `related_ids` point at. |
| `source` | enum | `github` \| `slack` \| `email` |
| `external_id` | string | GitHub issue number as a bare string, e.g. `"142"` (no `#`); null for seeded chat |
| `title` | string | short summary |
| `body` | text | full report text (also written to Files) |
| `priority` | enum \| null | `critical` \| `high` \| `normal` \| `low`; null until triaged |
| `repro_steps` | text (markdown) \| null | bullet list; null until triaged |
| `triage_reason` | text \| null | one-sentence AI triage rationale (the `reason` from §3); null until triaged |
| `status` | enum | `new` \| `triaged` \| `investigating` \| `resolved` |
| `related_ids` | string[] | ids of confirmed duplicates / related issues. No DB default — writers send `[]`. |
| `linked_prs` | string[] | PR identifiers that fix it (optional). No DB default — writers send `[]`. |
| `assignee` | string \| null | operator-assigned owner; null = Unassigned. Written by the App's human-override controls via `set_assignee`. |
| `source_account` | string \| null | the origin *within* a source — GitHub repo (`cli/cli`), Slack channel (`#eng-help`), mailbox (`support@`). The dimension the App's repo/workspace/mailbox switcher groups by (multi-source). |
| `created_at` | ISO datetime | system-managed (auto) |
| `updated_at` | ISO datetime | system-managed (auto) |

> **Live now:** this table exists on pod `forge` (`019f01ec-5992-732f-b395-a2b29fc87254`),
> seeded with 16 real `cli/cli` issues (`gh_*`). Dev B can read it directly — see the
> README "Connect to the live pod" section.

## 2. Files convention (powers dedup + RAG)

- One file per issue: path `/issues/{id}.md`, content = `# {title}\n\n{body}`.
- Product docs (optional) under `/knowledge/...`.
- Write: `pod.files.write_text(path, content)` (the SDK has `write_text`, not `write`).
- Search: `pod.files.search(query, scope_path="/issues", search_method="HYBRID")`.
- Indexing is **async**: a file is only searchable once it reaches `COMPLETED`
  status, so dedup-on-ingest must tolerate a brief delay (poll/retry).

## 3. Triage agent — output JSON (strict)

```json
{
  "priority": "critical | high | normal | low",
  "repro_steps": "- step one\n- step two",
  "reason": "one short sentence — evidence-based, NO fabricated percentages"
}
```
`normalize_priority` Function validates this → coerces unknown/missing priority to `normal`,
and persists `reason` to the `issues.triage_reason` column so the App can show *why* the AI
chose the priority.

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

## 7. `events` Table — audit / evidence trail

One row per thing that happened to an issue, rendered as a timeline on the detail view.

| Field | Type | Notes |
|---|---|---|
| `id` | string (PK) | `evt_<uuid4hex>` |
| `issue_id` | string | the `issues.id` this event belongs to |
| `kind` | enum | `ingested` \| `triaged` \| `linked` \| `investigated` \| `priority_changed` \| `assignee_changed` \| `status_changed` \| `note` |
| `actor` | enum | `system` (pipeline) \| `ai` (an agent) \| `operator` (a human in the App) |
| `summary` | text | one human-readable line, e.g. `AI triaged as Critical` |
| `detail` | text \| null | optional JSON string with structured before/after, e.g. `{"from":"high","to":"critical"}` |
| `created_at` | ISO datetime | system-managed (auto) — the timeline timestamp |

Writers (the only things that append events): `set_priority`, `set_assignee`, `set_status`
(operator overrides), and the backfill/ingest path (`ingested`/`triaged`/`linked`). The App
reads events with `records.list("events", {limit})` and filters by `issue_id` client-side; in
mock/seed mode it **synthesizes** the trail from the issue's own fields so the timeline always renders.

### Override Functions — input shapes

```json
// set_priority — validates against the priority enum, writes, logs a priority_changed event
{ "issue_id": "gh_142", "priority": "high" }
// set_assignee — writes assignee (empty/null = Unassigned), logs an assignee_changed event
{ "issue_id": "gh_142", "assignee": "alex" }
// set_status (existing) — now also logs a status_changed event
{ "issue_id": "gh_142", "status": "resolved" }
```
All three return `{ ..., ok: bool, error?: string }`; `ok:false` (no write) on an invalid enum value.

---

### Change log for this contract
- 2026-06-25 — initial freeze (Phase 0).
- 2026-06-26 — SDK reality check (Lane A, D1). Pinned `lemma-sdk==0.5.0`. Real
  facts that differ from earlier assumptions, now reflected above + in
  `.env.example`:
  - Import is `from lemma_sdk import Pod` (not `from lemma import Pod`).
  - Auth env vars are `LEMMA_TOKEN` + `LEMMA_POD_ID` (+ optional `LEMMA_BASE_URL`,
    `LEMMA_ORG_ID`), **not** `LEMMA_POD_URL` / `LEMMA_API_KEY`. A `lemma auth login`
    CLI session in `~/.lemma/config.json` also works.
  - Files use `write_text`; search is async (see §2).
  - Tables are created via `pod.tables.create(...)`; `id`, `created_at`,
    `updated_at` are auto-materialized system columns. `issues` is created with
    `enable_rls=False` (shared team table, not per-user).
  - No field names changed — the `issues`/triage/investigation shapes are intact.
- 2026-06-26 — table created live on pod `forge` and verified end-to-end. Two
  facts learned creating it; **no field renames**, so the seam is unchanged:
  - A custom string `id` PK **is** accepted, so the human-readable ids
    (`gh_142`, `iss_001`) in §1 stand exactly as written — `id` is NOT forced to a UUID.
  - JSON column defaults must be a scalar literal — the API rejects `default: []`.
    So `related_ids` / `linked_prs` have no column default; callers write `[]`
    explicitly on insert (ingest already does). File search can also 500
    transiently while a doc is mid-indexing — poll/retry, don't fail on first error.
- 2026-06-27 — trust controls & multi-source (POST-D5). **Additive, no renames.**
  `issues` gains nullable `assignee` + `source_account` (§1). New `events` audit
  table (§7) + override Functions `set_priority` / `set_assignee` (and `set_status`
  now logs an event). Un-cuts multi-repo from `DECISIONS.md`.
