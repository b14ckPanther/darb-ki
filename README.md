# Darb Ki

**Role in the universe:** The Watchtower.

Darb Ki is a defensive security research project. Terraform puts low-interaction honeypots (Cowrie for SSH/Telnet, OpenCanary for a few other protocols) on small isolated AWS instances in several regions. These fake servers look like easy targets. Real attackers find them within minutes. Every login attempt and every command they type is recorded.

A pipeline normalises the logs, strips and anonymises attacker identity for anything public, and runs an ML model that sorts each session into bots, crypto-miners and humans typing by hand. The result lands on a live 3D globe: attacks arc in from around the world, and you can click one to replay exactly what the attacker typed.

Safety comes first. The sensors **cannot open outbound connections to the internet**: they can only answer connections that attackers open. They never collect or redistribute malware. Attacker IPs never appear in public views. See `docs/ARCHITECTURE.md` §4 (egress rules) and `docs/VISION.md` §6 (legal and ethics note).

Status: planning package. Nothing is built yet. Progress lives in `docs/PROGRESS.md`.

## Stack

| Layer | Choice | Status |
|---|---|---|
| Honeypots | Cowrie 2.x (SSH 22, Telnet 23), OpenCanary 0.9.x (HTTP, FTP, MySQL, Redis) | fixed by brief (exact services proposed) |
| Sensor image | Packer-built Amazon Linux 2023 arm64 AMI | proposed, confirm with Nour in Phase 1 |
| Infrastructure | AWS (EC2, VPC, S3, IAM, Lambda, SQS, DynamoDB, CloudFront) via Terraform 1.x, AWS provider 6.x | fixed by roadmap (services proposed) |
| Log shipping | Vector on each sensor, to S3 over a VPC gateway endpoint (no internet egress) | proposed |
| Pipeline | Python 3.13 Lambdas (normalise, enrich, anonymise, classify, publish) | proposed |
| ML | scikit-learn + LightGBM, HDBSCAN clustering, exported to ONNX, run with onnxruntime | fixed: "ML classification", "attacker clustering"; libraries proposed |
| Frontend | Vite 7 + React 19 + TypeScript + Three.js (globe built on `three-globe` / `globe.gl`) | proposed |
| Hosting | Static site and public feed on S3 + CloudFront | proposed |
| CI | GitHub Actions: pytest, Vitest, Playwright + axe, `terraform test`, tflint, Trivy, Checkov, Infracost | proposed |

## Expected cost

About **$38 per month** with 3 sensor regions on-demand (about **$23** on spot), about **$12** with one region. Local development is $0. Breakdown and assumptions: `docs/ARCHITECTURE.md` §9. Nothing paid is deployed without Nour's explicit "yes".

**Teardown (deletes every cloud resource):**

```bash
make teardown        # runs: terraform -chdir=infra/envs/live destroy, then the leftover check
```

Full manual sequence in `docs/ARCHITECTURE.md` §10.

## Folder map (target, created from Phase 0)

```
darb-ki/
├── web/                     Vite + React + Three.js globe app
├── pipeline/                Python 3.13 package: normalise, enrich, anonymise, classify, publish
├── ml/                      training notebooks-as-scripts, features, eval reports, model cards
├── sensor/                  Cowrie + OpenCanary config templates, Vector config, Packer template
├── infra/
│   ├── modules/             sensor-region, pipeline, public-site, budget
│   ├── envs/live/           the real deployment (remote state)
│   ├── envs/bootstrap/      state bucket + lock table
│   └── tests/               terraform test files
├── lab/                     local Docker lab: isolated network, sensors, replay attacker
├── config/                  YAML: regions, ports, classes, anonymisation, thresholds, copy, seed
├── contracts/events/        JSON Schemas for universe events
├── docs/                    this planning package and later specs/plans
└── Makefile                 lab-up, test, plan, apply, teardown
```

## How to start

Open Claude Code in this folder and say:

> start Phase 0

The agent reads `CLAUDE.md`, then `docs/PLAN.md`, and works phase by phase. It asks Nour before anything outward-facing (repo creation, pushing to main, any paid `terraform apply`).

## Planning docs

| File | What |
|---|---|
| `CLAUDE.md` | Agent operating manual. The law. |
| `AGENTS.md` | Pointer for non-Claude agents |
| `docs/VISION.md` | Goals, non-goals, anti-goals, legal/ethics note, why this stack |
| `docs/ARCHITECTURE.md` | Components, egress rules, data flow, cost, teardown |
| `docs/UI_DESIGN.md` | Signature globe moment, screens, motion, art directions |
| `docs/INTEGRATION.md` | Events emitted to the universe |
| `docs/PLAN.md` | Phases 0 to 11, 0% to 100% |
| `docs/PROGRESS.md` | Ledger |
| `docs/DECISIONS.md` | ADR log |
| `docs/OPEN_QUESTIONS.md` | What only Nour decides |
| `docs/CONVENTIONS.md` | Code style, layout, tests, commits, PRs |

## How it fits the universe

Darb Budokai is the RPG that Nour's real life powers (`/Users/zangeel/Documents/GitHub/darb-budokai/`). Darb Ki is its Watchtower: attackers are invaders at the borders. It emits a daily summary and rare "human invader" events as versioned CloudEvents (`docs/INTEGRATION.md`). It works fully without Darb Budokai. Darb Enmacho can archive the same events, and Darb Kaioken can publish the write-up with honest numbers.
