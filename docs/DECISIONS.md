# Decision Log (ADR-lite)

Three lines per decision: **Decision / Why / Rejected.** This doc feeds the 25% "product judgment —
any wasted complexity?" score and the hiring track's "how they scoped and defended decisions."

---

### D-001 · Lemma is the entire backend
- **Decision:** Use Lemma Tables, Files, Agents, Workflows, Functions, App — no custom backend.
- **Why:** Lemma already provides them; rebuilding is wasted complexity (penalized) and costs SDK-utilisation points (15%).
- **Rejected:** FastAPI + Postgres + custom React. Reason: duplicates the platform we're graded on using.

### D-002 · No vector database
- **Decision:** Duplicate detection via `pod.files.search(search_method="HYBRID")`.
- **Why:** Files are auto-chunked + embedded; hybrid search is built in.
- **Rejected:** Qdrant / Pinecone / Weaviate / Milvus + embeddings pipeline. Reason: redundant, demo scale is ~20 issues not 10M vectors.

### D-003 · No Postgres / Redis of our own
- **Decision:** One `issues` Lemma Table; no cache layer.
- **Why:** Demo-scale data; Tables cover structured storage; no queue load to justify Redis.
- **Rejected:** 7-entity relational schema. Reason: hours of schema work that never appears on camera.

### D-004 · Read-only GitHub via PAT (no OAuth)
- **Decision:** Personal Access Token, read-only.
- **Why:** OAuth app registration + callbacks can eat half a day for zero demo value.
- **Rejected:** Full GitHub OAuth. GitHub is NOT a Lemma Surface, so this is the one connector we build.

### D-005 · Slack/Email via Surfaces or seed (not hand-built webhooks)
- **Decision:** Use Lemma Surfaces if time allows; otherwise seeded JSON into the same Table.
- **Why:** Surfaces include webhook ingress + identity resolution for free.
- **Rejected:** Hand-built FastAPI webhooks per source.

### D-006 · Evidence, not confidence percentages
- **Decision:** Investigation shows clickable evidence links, never a "91%" figure.
- **Why:** LLM-emitted percentages are uncalibrated theater; evidence is verifiable.
- **Rejected:** Confidence % UI from the original draft.

### D-007 · One persona, one hero loop
- **Decision:** Build for "Alex, founding engineer." Hero loop = ingest → triage+dedup → queue → investigate. Release Center is the only optional feature.
- **Why:** 35% problem-fit rewards a specific user; a working narrow loop beats five broken features.
- **Rejected:** Bug graph, analytics dashboard, command palette, multi-repo, CI/Sentry, breaking-change diff analysis.

---

## Scope & kill criteria (Phase 0 agreement)
- **Lanes:** Dev A = Lemma Core (pod/agents/workflows/functions/ingest). Dev B = App & Demo (app/seed/recording/writeup).
- **Workflow:** trunk-based on `main`, conventional commits, one commit per checklist box, pull-before-push, folder ownership avoids conflicts.
- **Contract-first:** `docs/contracts.md` is frozen; build both lanes against it in parallel.
- **Kill criteria:**
  - Drop Release Center on **D4 AM** if investigation isn't solid.
  - Switch to **pre-recorded** investigation if live run is flaky by **D5 noon**.
  - Any task >2× its estimate → stop, sync, re-scope.

### Open decisions (TBD)
- Slack/Email: Surfaces vs seed — decide by end of D2.
- Release Center: go/no-go — decide D4 AM (record here).
