# Progress ledger

Agents update this file after **every** task (one row) and at every phase boundary. It is the first thing read after a context reset. `git log` is the truth if they ever disagree; fix this file first.

**Overall:** 0% · **Current phase:** 0 (not started) · **Current branch:** none · **Last updated:** YYYY-MM-DD

**Cloud state:** nothing deployed · **Month-to-date AWS cost:** $0 · **Budget:** not created

## Phases

| Phase | Name | Weight | Status | Branch | Commit range | Skills used | Merged (Nour OK) |
|---|---|---|---|---|---|---|---|
| 0 | Repo bootstrap, CI, conventions | 5% | not started | `phase/00-bootstrap` | | | |
| 1 | Spec confirmation with Nour | 4% | not started | `phase/01-spec` | | | |
| 2 | Design system | 10% | not started | `phase/02-design-system` | | | |
| 3 | Globe and screens prototype on seed data | 14% | not started | `phase/03-ui-prototype` | | | |
| 4 | Sensors in the local lab + egress proof | 10% | not started | `phase/04-sensor-lab` | | | |
| 5 | Pipeline: ingest, anonymise, publish (local) | 12% | not started | `phase/05-pipeline` | | | |
| 6 | Terraform + first live region | 12% | not started | `phase/06-first-region` | | | |
| 7 | ML classification and clustering | 12% | not started | `phase/07-ml` | | | |
| 8 | Multi-region, daily stats, clans, outbox | 7% | not started | `phase/08-multi-region` | | | |
| 9 | Darb Budokai integration (optional) | 3% | not started | `phase/09-budokai` | | | |
| 10 | Hardening | 6% | not started | `phase/10-hardening` | | | |
| 11 | Docs, demo GIF, public launch | 5% | not started | `phase/11-launch` | | | |

Status values: `not started`, `in progress`, `blocked`, `in review`, `done`.
Overall % = sum of weights of `done` phases + (weight × completed tasks / total tasks) for the phase in progress.

## Task ledger (current phase)

| # | Phase | Task | Status | Commits (first..last) | Tests run → result | Skills used | Notes |
|---|---|---|---|---|---|---|---|
| 0.1 | 0 | Confirm repo name, visibility, licence with Nour | not started | | | | |

Example row:
`| 4.4 | 4 | nftables output drop for cowrie uid | done | a1b2c3d..e4f5a6b | uv run pytest sensor/tests/test_nftables.py → 9 passed | superpowers:test-driven-development, security-review | ruleset in sensor/nftables/ki.nft |`

## Rulings (decisions made without Nour)

Every time an agent decides something Nour has not decided. If "cost if wrong" is high, or it touches safety, stop and ask instead.

| Date | Phase | Ruling | Why | Cost if wrong (low/med/high + what breaks) | Confirmed by Nour? |
|---|---|---|---|---|---|
| | | | | | |

## Cloud actions log (every apply, destroy, AMI build, kill switch)

| Date | Action | Nour's "yes" (where/when) | Regions | Infracost / actual cost | Result |
|---|---|---|---|---|---|
| | | | | | |

## Safety log (egress probes, tripwire hits, abuse reports)

| Date | Check | Result | Follow-up |
|---|---|---|---|
| | | | |

## UI approvals

| Date | Screen | Screenshot path | Nour's verdict | Follow-ups |
|---|---|---|---|---|
| | | | | |

## Blockers and waiting on Nour

| Since | What | Asked how | Status |
|---|---|---|---|
| | | | |

## Session log

Short notes per session (2 to 4 lines): what was done, where it stopped, next step.

- YYYY-MM-DD:
