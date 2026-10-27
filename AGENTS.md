# AGENTS.md

This repo's full agent manual is **`CLAUDE.md`**. Every agent tool (Codex, Cursor, Copilot, Gemini, Aider, others) must read and follow it. This is a summary; if anything differs, `CLAUDE.md` wins.

## Non-negotiable rules

1. **No AI contributors.** "Never add "Co-Authored-By" or any other AI attribution line to commit messages, pull request descriptions, or any other text, in any project. Commit messages end with the last line of the actual description." Every commit is authored and committed as `Nour Alden Mousa <nmcryptoinvest@gmail.com>` (`git config user.name/user.email` set in the repo). Never write the word "claude" in a commit message.
2. **Defensive only.** Honeypot sensors can never open outbound connections (only HTTPS to their region's S3 gateway endpoint). Never loosen egress rules, never hack back, never collect or redistribute malware (hash, then delete). Attacker IPs never appear in public views. See `docs/ARCHITECTURE.md` §4 and §7.
3. **No hardcoded data.** Regions, ports, personas, labels, thresholds, copy and seed content live in `config/**.yaml`, env vars or the database. Fixtures only in tests and the labelled demo mode.
4. **Secrets** only in env vars, a git-ignored `.env`, or SSM; keep `.env.example` current. CI uses OIDC, no static AWS keys.
5. **Original assets only** (Google Fonts OK). Log third-party assets in `ASSETS.md`.
6. **Ask Nour first** before creating/publicising the repo, pushing to `main`, merging, publishing, any real `terraform apply`/`packer build`/`destroy`, or deleting. Commit locally freely, one branch per phase (`phase/NN-name`), small honest commits.
7. **TDD.** Failing test first. moto for AWS, `terraform test` with mock providers, sanitised fixtures with documentation-range IPs. No live AWS or internet in CI.
8. **UI first.** Design system, then globe prototype on seed data approved screen by screen, before pipeline/infra work. Responsive, keyboard accessible, reduced motion, WCAG AA. Native-feel on mobile, one modern SVG icon set, **no emoji anywhere**.
9. **Skills.** Check the installed skill list before every task and invoke every matching one (table in `CLAUDE.md` §2, per-phase list in `docs/PLAN.md`). Record skills used in `docs/PROGRESS.md`.
10. **Workflow:** brainstorm → spec (`docs/specs/`) → plan (`docs/plans/`) → execute with ledger (`docs/PROGRESS.md`) → whole-branch review → finish.

## Before every push

```bash
git log --format='%an %ae%n%cn %ce' | sort -u          # only: Nour Alden Mousa nmcryptoinvest@gmail.com
git log --format=%B | grep -ciE 'co-authored|claude|anthropic|generated with'   # must be 0
make check-private check-emoji
```

## Resume after a reset

Read `CLAUDE.md`, then `docs/PROGRESS.md`, then `git log --oneline -20`, then the current phase in `docs/PLAN.md`.
