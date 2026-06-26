# Forge — Execution Framework & Mega Checklist
### Team of 2 · June 25–30, 2026 · one commit per ticked box

> How to read this:
> - **`[A]`** = Dev A (Lemma Core / backend). **`[B]`** = Dev B (App / Ingestion / Demo). **`[A+B]`** = sync, do together.
> - **🟢 PARALLEL** = A and B work at the same time, no blocking. **🔴 BLOCKING** = must finish before the dependent box starts.
> - **🔗 CONTRACT** = a shared interface; agree it together *before* splitting, then both build against it.
> - Each box ends with a suggested commit: `commit: \`type(scope): msg\``. Tick the box → make that commit → push. Small commits, often.

---

## PART 1 — The frameworks you're missing

You have a *product* plan (PRD.md). You're missing the *engineering process* that lets 2 people move fast without stepping on each other. These are the gaps to close in Phase 0, ranked by impact.

### 1. Contract-first development (THE thing that unblocks parallel work) 🔗
The reason 2 devs stall is waiting on each other. Kill that by **freezing the data contract on Day 1** and building against it:
- The `issues` Table schema (field names + types).
- The triage agent's **JSON output shape** (`{priority, repro_steps, related_ids}`).
- The investigation workflow's **result shape** (`{hypothesis, evidence:[{type,label,url}]}`).
Once these are agreed and committed, **B builds UI against mock data in that exact shape** while **A builds the real pod**. They meet at the contract. This is the single highest-leverage practice here.

### 2. Git workflow (so "one commit per box" actually works)
- **Trunk-based on `main`.** No long-lived branches for a 6-day, 2-person sprint — they diverge and merge-hell eats a day.
- **Folder ownership avoids conflicts:** A lives in `pod/` + `ingest/github`, B lives in `app/` + `seed/`. Different files = no conflicts.
- **Conventional commits:** `feat(pod): add issues table`, `fix(app): repro list overflow`, `chore: env example`. Scopes: `pod, app, agent, wf, fn, ingest, seed, docs, chore`.
- **Pull before you push. Push after every box.** Your work must survive a dead laptop — the repo is the backup.
- Optional: protect `main` only loosely; speed > ceremony here.

### 3. Secrets & env hygiene (a leaked key is a visible red flag to judges + hiring partners)
- `.env` is **git-ignored**; commit only `.env.example` with empty keys.
- Model API key + GitHub PAT live in env vars, never in code, never in a commit. Scan history before submitting.

### 4. Seed/mock data strategy (deterministic demos + B never blocked)
- A `seed/` folder of fixed JSON: ~20 GitHub-style issues (incl. 2–3 genuine duplicates), ~5 Slack msgs, ~3 emails, a few "merged PRs."
- The recording runs on this curated set so it's the same every take. Real GitHub fetch is shown live once; seed data carries the rest.

### 5. Vertical-slice / demo-driven development
Build the **thinnest end-to-end path first** (one issue → triaged → shown in UI), then deepen. Never spend 2 days on a component with no end-to-end path. At every EOD you should be able to *run the loop*.

### 6. A "run-it-all" smoke script + health check
- `scripts/smoke.*` that runs the core loop start→finish and prints PASS/FAIL.
- Run it before every demo take and before submitting. This is your "does the core loop work" insurance (25% of score).

### 7. Decision log — `DECISIONS.md` (ADR-lite)
Every scope cut and tech choice gets 3 lines: *decision / why / what we rejected.* This feeds two scored things directly: the **25% product-judgment** ("any wasted complexity?") and the **hiring track** ("how they scoped and defended decisions"). Your §8 cut-list from the PRD seeds it.

### 8. Daily cadence + integration checkpoints
- **AM (10 min):** what each of you ships today, where you'll integrate.
- **PM (the 🔁 checkpoints below):** merge both lanes, run the smoke script, fix integration breaks *same day*.

### 9. Time-boxing & kill criteria (decide the triggers NOW, not in the panic)
- Release Center is the **only** optional feature — drop it D4 AM if investigation isn't solid.
- If the live investigation is flaky by D5 noon → switch to the **pre-recorded** run (rules allow recordings).
- Any single task >2× its estimate → stop, ping teammate, re-scope.

### 10. README / runbook
A `README.md` that takes a stranger from clone → running in <10 steps. Needed for submission credibility *and* the Project Track (top-10 templates get published).

> Optional but nice: mirror this checklist into a **GitHub Projects board** (one card per box) so progress is visible and you can defend velocity in interviews.

---

## PART 2 — The mega checklist

### Lane ownership
- **Dev A — Lemma Core:** pod, Tables, Files, Agents, Workflows, Functions, dedup, GitHub fetch.
- **Dev B — App & Demo:** Lemma App UI, ingestion glue, seed data, demo recording, writeup, README.

### Repo layout (create in Phase 0)
```
forge/
  pod/        agents/  workflows/  functions/  tables/   # [A]
  app/                                                    # [B]
  ingest/     github/        # [A]      seed/ loader      # [B]
  seed/       *.json                                      # [B]
  scripts/    smoke.*                                     # [A+B]
  docs/       PRD.md  DECISIONS.md  EXECUTION.md  demo-script.md
  .env.example   README.md   .gitignore
```

---

## ✅ PHASE 0 — Setup (🔴 BLOCKING · ~1 hr · do together, June 25 AM) — DONE

- [x] **[A+B]** Create GitHub repo `forge`, both have push access. — commit: `chore: init repo` _(live at KuantumKnight/forge, private; still TODO: add teammate as collaborator)_
- [x] **[A+B]** Add `.gitignore` (env, node_modules, __pycache__, .venv). — commit: `chore: add gitignore`
- [x] **[A+B]** Scaffold folder layout above (empty dirs w/ `.gitkeep`). — commit: `chore: scaffold project structure`
- [x] **[A+B]** `.env.example` with `MODEL_API_KEY=`, `GITHUB_PAT=`, `LEMMA_*=`. — commit: `chore: add env example`
- [x] **[A+B]** Copy `PRD.md` into `docs/`; create empty `DECISIONS.md`. — commit: `docs: add PRD and decisions log`
- [x] **[A+B]** 🔗 **CONTRACT:** write `docs/contracts.md` — `issues` table fields, triage JSON shape, investigation result shape. — commit: `docs: freeze data contracts`
- [x] **[A+B]** Agree lane ownership + the kill-criteria from Part 1 §9; note in `DECISIONS.md`. — commit: `docs: record scope and kill criteria`

> ✅ Exit Phase 0: repo runs `git status` clean for both, contract frozen. **Now split.**

---

## ✅ DAY 1 — June 25 PM · Spine (🟢 PARALLEL after Phase 0) — DONE

### Lane A — Lemma pod + ingestion
- [x] **[A]** Install Lemma SDK, `Pod.from_env()` connects. — commit: `feat(pod): bootstrap pod connection` _(live: pod `forge` 019f01ec…)_
- [x] **[A]** Define `issues` Table per contract. — commit: `feat(pod): add issues table` _(12 cols incl. system created_at/updated_at; custom string `id` PK)_
- [x] **[A]** Smoke: create a record + read it back. — commit: `test(pod): issues table round-trip`
- [x] **[A]** Write a Markdown File + `files.search("HYBRID")` returns it. — commit: `feat(pod): verify hybrid file search`
- [x] **[A]** `github_fetch` Function: pull open issues from a public repo via PAT. — commit: `feat(fn): github_fetch issues` _(verified live: open issues from cli/cli)_
- [x] **[A]** Map fetched issues → `issues` rows + write bodies to Files. — commit: `feat(ingest): github issues into table+files` _(16 rows + 16 files; idempotent re-run)_

### Lane B — App skeleton (🟢 against mock data, no dependency on A)
- [x] **[B]** Init Lemma App (single-file HTML or React per SDK docs); it serves. — commit: `feat(app): bootstrap lemma app` _(single-file HTML app `app/index.html`; SDK boot from injected `__LEMMA_CONFIG__`, graceful mock-mode fallback; serves 200 locally)_
- [x] **[B]** `seed/issues.json` ~20 items matching the contract (incl. dup pairs). — commit: `feat(seed): sample issues fixture` _(20 items, exact contract §1 fields; 3 symmetric dup pairs via `related_ids` (gh_142↔iss_003, gh_158↔iss_007, gh_171↔iss_011); priority spread 3/5/5/4 + 2 null; github/slack/email sources)_
- [x] **[B]** Priority Queue screen renders cards from mock data (title, priority badge). — commit: `feat(app): priority queue from mock` _(DataSource.listIssues() seam reads seed/issues.json in mock mode; renders 20 cards with title + id + source + priority badge; HTML-escaped)_
- [x] **[B]** Critical-first sort + priority color coding. — commit: `feat(app): sort and color by priority` _(sortCriticalFirst: critical→high→normal→low→untriaged, updated-desc tiebreak; per-priority badge tint + colored left rail on each card)_
- [x] **[B]** Empty/loading states. — commit: `feat(app): queue loading and empty states` _(shimmer skeleton rows while loading (aria-busy, reduced-motion safe); "Queue is clear" empty state; actionable error state with Retry → boot())_

- [x] 🔁 **[A+B] CHECKPOINT (EOD D1):** point B's queue at A's real Table; run smoke. — commit: `feat(app): read issues from live table` _(app deployed to pod → live at https://forge.apps.lemma.work; reads the live `issues` Table (16 real rows) via injected `__LEMMA_CONFIG__`; smoke PASS — connection / record round-trip / HYBRID search; all 16 rows expose every app-rendered field)_

---

## ☐ DAY 2 — June 26 · Triage works (🟢 PARALLEL)

### Lane A — Triage agent
- [x] **[A]** Define `triage` agent (role, scoped to `issues` + Files). — commit: `feat(agent): triage agent definition` _(bundle `pod/agents/triage`: POD toolset, read-only grants `issues:read` + `/issues:read`, strict `output_schema` {priority,repro_steps,reason} per contract §3; dry-run import OK. D-011 records the bundle-authoring decision.)_
- [x] **[A]** Prompt: output strict JSON `{priority, repro_steps}`. — commit: `feat(agent): triage classify + repro prompt` _(instruction.md: priority rubric (critical/high/normal/low, default normal when unclear), repro-steps rules (reporter's steps or explicit "no repro" bullet, no fabrication), evidence-based reason, no fake %. Imported + live-tested on a sample crash → correct `critical` verdict, schema-conformant JSON via `final_result` tool.)_
- [x] **[A]** `normalize_priority` Function: validate JSON → enum, default Normal. — commit: `feat(fn): normalize_priority validator` _(API fn `pod/functions/normalize_priority`, granted issues:read,write — the single triage writer. Coerces priority to the contract enum (unknown/missing → normal), writes priority + repro_steps + status='triaged' back. Verified live: `high` kept (coerced=no), `P0-urgent`→`normal` (coerced=yes); both rows persisted triaged.)_
- [x] **[A]** Run triage over a conversation; write results back to row. — commit: `feat(agent): triage write-back to issues` _(`ingest/triage/run_triage.py`: opens an agent conversation per issue, polls to COMPLETED, extracts the `final_result` verdict (text-JSON fallback), calls `normalize_priority` to write back. Verified live: `gh_13571` → priority=low, status=triaged, repro persisted.)_
- [x] **[A]** Batch: triage all newly-ingested issues. — commit: `feat(ingest): batch triage on ingest` _(`triage_batch()` lists status='new' issues and triages each; one failure (transient read timeout) never aborts the run — the row stays 'new' for retry. Ran live: 12/13 first pass, retried the 1 timeout → all 16 issues now `triaged` (mix of high/normal/low).)_
- [x] **[A]** Log raw agent output to a file for debugging. — commit: `chore(agent): log triage outputs` _(each run writes `logs/triage/<issue_id>.json` (gitignored): prompt + parsed verdict + conversation_id + full message transcript incl. THINKING/final_result. Logging is best-effort — a log failure never breaks triage. Verified on gh_13571.)_

### Lane B — Ingestion glue + detail view
- [x] **[B]** `seed/slack.json` + `seed/email.json` fixtures. — commit: `feat(seed): slack and email fixtures` _(4 Slack + 4 email rows, exact `issues` contract shape, includes duplicate links to GitHub issues and untriaged examples for loader/triage.)_
- [x] **[B]** Seed loader writes Slack/email into the `issues` Table (same shape). — commit: `feat(ingest): load seed feedback into table` _(`ingest/seed/load_feedback.py` validates fixtures with `--dry-run`, upserts rows idempotently through the Lemma SDK, and writes `/issues/{id}.md` Files. Verified live: 8 rows loaded into `issues` (8 new, 0 updated).)_
- [x] **[B]** Issue Detail view: title, body, source, priority, repro steps. — commit: `feat(app): issue detail view` _(queue cards open an in-app detail screen with title, report body, source/id/priority metadata, repro steps, and a back-to-queue control; script parse check PASS.)_
- [x] **[B]** Source badges (GitHub / Slack / Email). — commit: `feat(app): source badges` _(queue + detail render source-specific `GitHub`, `Slack`, and `Email` badges with distinct compact styling; inline script parse check PASS.)_

- [x] 🔁 **[A+B] CHECKPOINT (EOD D2):** real triaged data (incl. seeded) shows priority+repro in detail view; smoke passes. — commit: `test: triage end-to-end smoke` _(all 24 live issues now triaged across github/slack/email (incl. the 8 seeded Slack/email rows); `scripts/smoke_triage.py` = SMOKE PASS: coverage (all triaged rows have valid priority enum + non-empty repro, all 3 sources present) + live loop (creates a throwaway crash issue → real triage agent → `critical` + repro written back → cleaned up). Detail view (`app/index.html`) renders `issue.priority` + `issue.repro_steps` from the live table (reads verified at D1 checkpoint).)_

---

## ☐ DAY 3 — June 27 · Queue + dedup (🟢 PARALLEL)

### Lane A — Duplicate detection
- [ ] **[A]** On new issue, `files.search(text, "HYBRID")` top-5. — commit: `feat(pod): similarity search on ingest`
- [ ] **[A]** Single LLM YES/NO confirm step for the top hit. — commit: `feat(agent): duplicate confirmation`
- [ ] **[A]** Write confirmed matches to `related_ids` on both rows. — commit: `feat(pod): link related issues`
- [ ] **[A]** Verify against the known dup pairs in seed data. — commit: `test(pod): dedup catches seeded duplicates`

### Lane B — Queue polish
- [ ] **[B]** "N related" badge on cards (reads `related_ids`). — commit: `feat(app): related count badge`
- [ ] **[B]** Related issues list inside detail view, clickable. — commit: `feat(app): related issues panel`
- [ ] **[B]** Filter by priority / source. — commit: `feat(app): queue filters`
- [ ] **[B]** Start `docs/demo-script.md` (storyboard from PRD §7). — commit: `docs: draft demo script`

- [ ] 🔁 **[A+B] CHECKPOINT (EOD D3):** open a critical bug → see real "3 related"; first dry-run of demo steps 1–3. — commit: `test: dedup visible in app`

---

## ☐ DAY 4 — June 28 · AI Investigation Workflow (the hero) (🟢 PARALLEL)

### Lane A — Investigate workflow
- [ ] **[A]** Define `investigate` Workflow with a FORM node taking `issue_id`. — commit: `feat(wf): investigate workflow skeleton`
- [ ] **[A]** Node: stack-trace / error reasoning over issue body. — commit: `feat(wf): stacktrace analysis node`
- [ ] **[A]** Node: related recent commits via `github_fetch`. — commit: `feat(wf): related commits node`
- [ ] **[A]** Node: similar past issues via Files search. — commit: `feat(wf): similar issues node`
- [ ] **[A]** Synthesis node → `{hypothesis, evidence:[{type,label,url}]}` per contract. — commit: `feat(wf): synthesize root-cause hypothesis`
- [ ] **[A]** Cap to 3 evidence sources; ensure <15s typical. — commit: `perf(wf): cap evidence sources`

### Lane B — Investigation UI
- [ ] **[B]** "Investigate" button on detail view → triggers workflow run. — commit: `feat(app): trigger investigation`
- [ ] **[B]** Progress/steps indicator while running. — commit: `feat(app): investigation progress view`
- [ ] **[B]** Evidence cards with clickable commit/issue links. — commit: `feat(app): evidence cards with links`
- [ ] **[B]** Hypothesis summary block (no fake %, evidence only). — commit: `feat(app): root-cause summary`

- [ ] 🔁 **[A+B] CHECKPOINT (EOD D4):** `investigate <id>` live → cited hypothesis in UI. **Record a backup take now.** — commit: `test: investigation end-to-end`
- [ ] **[A+B]** Decide: Release Center IN or OUT (kill criteria). Note in `DECISIONS.md`. — commit: `docs: release-center go/no-go`

---

## ☐ DAY 5 — June 29 · Flourish OR harden (🟢 PARALLEL)

### If Release Center is GO
- [ ] **[A]** `github_fetch` extended: merged PRs since last tag. — commit: `feat(fn): fetch merged PRs`
- [ ] **[A]** `release_notes` agent: group PRs (Added/Fixed/Changed) + draft. — commit: `feat(agent): release notes drafting`
- [ ] **[A]** `prepare_release` Workflow (FORM node: version). — commit: `feat(wf): prepare_release workflow`
- [ ] **[B]** Release view: command/button → grouped notes, editable. — commit: `feat(app): release notes view`

### Regardless (hardening — both lanes)
- [ ] **[A]** Error handling: agent fails → graceful fallback, no UI crash. — commit: `fix(pod): graceful agent failure`
- [ ] **[A]** Finalize `scripts/smoke` covering the full loop. — commit: `test: full-loop smoke script`
- [ ] **[B]** Curate the exact demo dataset (deterministic). — commit: `feat(seed): finalize demo dataset`
- [ ] **[B]** UI polish: spacing, the one "screenshot" moment looks clean. — commit: `style(app): demo polish`
- [ ] **[B]** Write `README.md` runbook (clone → run). — commit: `docs: add README runbook`
- [ ] **[A+B]** Fill in `DECISIONS.md` cut-list + rationale. — commit: `docs: complete decision log`

- [ ] 🔁 **[A+B] CHECKPOINT (EOD D5):** full loop stable; smoke PASS; **2 backup recordings exist.** — commit: `test: pre-submission smoke pass`

---

## ☐ DAY 6 — June 30 · Submit (🔴 do together)

- [ ] **[A+B]** Final run-through on the curated dataset (twice). — _(no commit; rehearsal)_
- [ ] **[B]** Record the 3-min screen recording (PRD §7 storyboard). — commit: `docs: add final demo recording link`
- [ ] **[B]** Writeup: problem + approach + "what we cut & why" (from DECISIONS.md). — commit: `docs: submission writeup`
- [ ] **[A]** 🔒 Scan git history for leaked keys; rotate if any. — commit: `chore: security pass on secrets`
- [ ] **[A+B]** Tag the submission. — commit: `chore: tag v1.0-submission` → `git tag v1.0-submission && git push --tags`
- [ ] **[A+B]** Submit the form (problem, approach, recording, team details) **before deadline**.
- [ ] **[A+B]** Confirm submission received; post in Discord if needed.

---

## Definition of Done (gate before you call it submitted)
- [ ] Real GitHub issues + seeded Slack/email land in `issues` Table.
- [ ] Every issue has AI `priority` + `repro_steps`.
- [ ] Dedup links ≥1 real duplicate pair, visible in App.
- [ ] Priority Queue: critical-first, repro + "N related".
- [ ] `investigate <id>` → hypothesis + ≥2 clickable evidence links (<15s or recorded).
- [ ] Smoke script PASSES.
- [ ] 3-min recording + writeup done; Lemma pod shown on camera.
- [ ] No secrets in git history.

---

## Parallelism cheat-sheet (who's blocked on whom)
- **Day 1:** fully parallel — B on mock data, A on real pod. Only the EOD checkpoint joins them.
- **Day 2–4:** A builds the brain (agents/workflow), B builds the face (UI) against the frozen contract. They integrate only at the 🔁 EOD checkpoint.
- **The contract is the seam.** As long as neither side changes a field name without telling the other (and updating `docs/contracts.md` + committing), you never block each other.
- **If A slips,** B keeps building against mock/seed data and demo polish — never idle.
- **If B slips,** A's loop still works via CLI; worst case the demo shows more CLI and less UI (still valid — polish is optional per rules).
