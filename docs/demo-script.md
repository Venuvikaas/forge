# Forge 3-Minute Hackathon Judge Demo Script

> Goal: demonstrate the full Forge loop in 3 minutes with two developers doing voiceover. Keep the screen moving, but do not rush the words. Dev A owns the product story; Dev B owns the technical proof and feature callouts.

## Setup Before Recording

- Open the Forge app: `https://forge.apps.lemma.work`.
- Have the Lemma pod open in another tab/window if possible.
- Start on the Forge queue with `gh_142` visible near the top.
- If live pod auth is flaky, use seed/sample mode. The UI shows the same issue shape and the `source-pill` will say `seed data` or `sample data`.
- Preferred demo issue: `gh_142`, the `gh pr create` nil-pointer crash, linked to Slack report `iss_003`.
- Backup issue: `gh_158`, the SSO/token failure, linked to email report `iss_007`.
- If the live investigation workflow is slow, use the already saved/sample investigation result. Say "this is the captured run result from the same workflow."

## Timing Plan

| Time | Screen | Speaker | Voiceover |
|---:|---|---|---|
| 0:00-0:08 | Show Forge top bar and full three-pane cockpit. | Dev A | "This is Forge: an AI bug triage and investigation cockpit for a founding engineer who wakes up to bug reports scattered across GitHub, Slack, and support email." |
| 0:08-0:18 | Point to queue, source tags, priority chips, critical count gauge, live/seed pill. | Dev A | "The problem is not just fixing code. The problem is deciding what matters first, spotting duplicate reports, and finding enough evidence to start a fix without losing the morning." |
| 0:18-0:30 | Click source tabs: All, GitHub, Slack, Email. Open account dropdown showing repo/channel/mailbox. | Dev B | "Forge ingests all of those sources into one Lemma `issues` Table. GitHub issues, Slack reports, and support emails keep their source labels and accounts, but land in the same ranked queue." |
| 0:30-0:42 | Use priority filter and search box briefly; clear filters. | Dev B | "The left pane is an operator queue: critical-first sorting, source filters, repo/channel/mailbox filtering, text search, status, assignee, and related-report counts. Alex is no longer manually sorting a pile." |
| 0:42-0:55 | Select `gh_142`. Show center issue summary. | Dev A | "I will open this critical GitHub report: `gh_142`. Forge shows the report identity, source, priority, status, assignee, and the AI triage reason right at the top." |
| 0:55-1:08 | Scroll center pane through Report and Reproduction. | Dev A | "The triage agent does not just stamp a label. It returns strict JSON: priority, reproduction steps, and a one-sentence reason. A validator writes that result back, so the agent is judging, not directly mutating state." |
| 1:08-1:22 | Show Related reports section. Click `iss_003` if visible, then back to `gh_142`. | Dev B | "Duplicate detection uses Lemma Files, not a separate vector database. Every report is written as Markdown under `/issues`, HYBRID search finds similar reports, a dedup agent confirms whether they are the same bug, and `link_related` writes symmetric links." |
| 1:22-1:36 | Open the three-dot menu; show priority, assignee, status controls. Change nothing or make one safe override if demo data allows. | Dev A | "Forge also keeps humans in control. The three-dot menu lets the operator override priority, assignee, or status. In live mode those writes go through granted Lemma Functions like `set_priority`, `set_assignee`, and `set_status`." |
| 1:36-1:46 | Point to audit timeline in right pane. | Dev B | "Every important action becomes an event: ingested, triaged, linked, investigated, and operator overrides. That audit timeline is built from the `events` Table, with a synthesized fallback for demo data." |
| 1:46-1:58 | Click `Investigate`. Show animated investigation status tree. | Dev A | "Now we run the hero workflow: investigate. The UI shows the workflow phases instead of hiding the work: analyze stack trace, find related commits, find similar issues, ground source evidence, then synthesize." |
| 1:58-2:16 | Show completed hypothesis card. | Dev A | "The output is a root-cause hypothesis, but the rule is evidence over confidence scores. Forge names the likely source of the crash and explains why using the gathered signals." |
| 2:16-2:34 | Show evidence cards and click/hover a source link if safe. | Dev B | "The investigation workflow combines deterministic Functions with one synthesis Agent. It gathers stack-trace signals, related commits, similar reports, and real repository source. The synthesis agent may cite only evidence it was given." |
| 2:34-2:48 | Show Proposed fix card, verified pill, file citation, unified diff, Copy diff button. | Dev B | "Because Forge grounded the suspected symbol in real `cli/cli` source, it can render a small proposed unified diff. The patch is anchored to actual fetched lines, and the Copy diff button makes it usable by the developer." |
| 2:48-3:04 | Switch to Lemma pod/resources or README architecture diagram. Show Tables, Files, Agents, Functions, Workflow, App. | Dev A | "The backend is Lemma: Tables for issue and event state, Files for hybrid search, Agents for triage and synthesis, Functions for guarded writes and evidence gathering, a Workflow for investigation, and this App for the operator cockpit." |
| 3:04-3:15 | Return to Forge queue on selected critical issue. | Dev A | "That is the product promise: Forge makes the next critical bug, the duplicate context, the source evidence, and the first fix direction the first thing Alex sees." |
| 3:15-3:20 | Optional final sentence if the recording allows it. | Dev B | "We deliberately skipped custom databases, vector infrastructure, fake confidence scores, and broad dashboards so the core loop is real and judgeable." |

## Tight 3-Minute Cut

If the recording must be exactly under 3:00, cut these first:

- Skip changing source tabs; just say the sources are unified while pointing at tags.
- Do not make an override; only open the three-dot menu.
- Do not click evidence links; point to them.
- Replace the final Lemma pod tab with the README architecture diagram if switching tabs is slow.
- End at 2:58 with: "Forge makes the next critical bug and the evidence to fix it the first thing Alex sees."

## Detailed Feature Checklist To Mention Or Show

- Unified queue for GitHub, Slack, and email reports.
- Live pod / seed data indicator in the top bar.
- Critical-count furnace gauge and total queue count.
- Priority chips: critical, high, normal, low, untriaged.
- Source tags and account labels: repo, channel, mailbox.
- Source switcher tabs: All, GitHub, Slack, Email.
- Account dropdown for repo/channel/mailbox filtering.
- Priority filter, text search, and clear filters.
- Three persistent panes: queue, issue summary, investigation/evidence.
- AI triage reason displayed, not just the verdict.
- Reproduction steps generated by triage.
- Related reports panel powered by dedup links.
- Human override menu for priority, assignee, and status.
- Guarded write Functions for operator overrides.
- Audit timeline with system, AI, and operator events.
- Investigate button and live/captured workflow progress.
- Workflow phases: stack trace, commits, similar issues, source evidence, synthesis.
- Root-cause hypothesis card.
- Evidence cards with clickable URLs.
- Source-grounded proposed fix only when real source evidence exists.
- Verified-against-real-source badge.
- Unified diff rendering with add/delete highlighting.
- Copy diff button.
- Saved investigation hydration so results survive refresh in live mode.
- Light/dark theme toggle; mention only if there is spare time.
- Responsive app behavior; mention only if judges ask.

## Dev A Full Lines

Use these if Dev A wants a continuous script.

"This is Forge: an AI bug triage and investigation cockpit for a founding engineer who wakes up to bug reports scattered across GitHub, Slack, and support email. The real pain is not only fixing bugs; it is deciding what matters first, spotting duplicates, and gathering enough evidence to start a fix.

Forge turns that messy stream into one ranked queue. I am opening `gh_142`, a critical GitHub report. The center pane shows the source, status, assignee, AI triage reason, original report, reproduction steps, and related reports. The triage agent returns strict JSON: priority, reproduction steps, and a reason. A validator writes the result back, so the agent is not directly mutating state.

Forge also keeps the human operator in control. From the three-dot menu, Alex can override priority, assignee, or status. Those changes go through granted Lemma Functions and show up in the audit timeline.

Now we run the hero workflow: investigate. The right pane shows each phase: analyze stack trace, find related commits, find similar reports, ground source evidence, and synthesize. The result is not a fake confidence score. It is a source-grounded hypothesis with evidence and, when real source lines are found, a proposed fix.

That is the product promise: Forge makes the next critical bug, the duplicate context, the evidence, and the first fix direction the first thing Alex sees."

## Dev B Full Lines

Use these if Dev B wants a continuous script.

"Technically, Forge is built on Lemma instead of a custom backend. The queue is a Lemma `issues` Table. Every raw report is also written to Lemma Files under `/issues`, so HYBRID search gives us duplicate detection and investigation retrieval without a separate vector database.

For deduplication, Forge searches similar reports, asks a read-only dedup agent whether they describe the same underlying bug, then writes symmetric links through a Function. That is why a GitHub crash can be connected to a Slack report or support email.

For investigation, the Lemma Workflow combines deterministic Functions with one synthesis Agent. Functions extract stack-trace signals, fetch related commits, find similar evidence, and ground the suspected symbol in real repository source. The synthesis Agent can only cite the evidence it receives.

When source evidence exists, Forge renders a proposed unified diff anchored to actual fetched lines. The developer can inspect the file citation, review the rationale, and copy the diff. The audit timeline records the full path: ingested, triaged, linked, investigated, and any operator override.

So the SDK story is visible in the product: Tables for state, Files for hybrid search, Agents for judgment, Functions for guarded writes, Workflows for evidence gathering, and a Lemma App for the operator UI."

## Backup Narration For Slow Investigation

If the live run does not complete during recording, use this line while showing the saved/sample result:

"For the recording, I am showing the captured result from the same investigation workflow. The live workflow path is the same: stack-trace analysis, commit search, similar reports, source grounding, then synthesis. We keep this fallback because judge recordings are time-boxed, but the artifact still shows the real workflow output contract."

## What Not To Say

- Do not call the product "Gappy"; Gappy AI is the organizer. The product is Forge.
- Do not claim release notes are in the final build unless you are explicitly showing them.
- Do not say "confidence score"; the product deliberately uses evidence links instead.
- Do not imply Slack/email OAuth is live; say seeded Slack/email reports unless real connectors are connected.
- Do not call the proposed diff an automatically merged fix. It is an inspectable starting point for the developer.
