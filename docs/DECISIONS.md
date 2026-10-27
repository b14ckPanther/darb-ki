# Decisions (ADR log)

Format: each ADR has a status (`accepted` = fixed by Nour's roadmap or the hard rules; `proposed` = confirm with Nour in Phase 1), context, decision and consequences. New ADRs are appended; superseded ones are marked, never deleted.

---

## ADR-001: Defensive only; sensors can never initiate outbound connections
**Status:** accepted (hard rule 9 and the project brief)
**Context:** honeypots attract attackers who will try to use the host to attack others.
**Decision:** seven layers of egress control (ARCHITECTURE §4), tested in CI and in the real cloud; tripwire with automatic quarantine.
**Consequences:** sensors cannot be administered over the network or fetch updates; they are immutable and rebuilt from AMIs. No feature that needs sensor egress may be built.

## ADR-002: No malware collection or redistribution
**Status:** accepted (brief)
**Decision:** hash and delete uploaded/downloaded files on the sensor; publish hashes only; no third-party uploads.
**Consequences:** no malware analysis features; classification relies on behaviour, not payloads.

## ADR-003: Attacker IPs never appear in public views
**Status:** accepted (brief)
**Decision:** keyed pseudonyms, codenames, coarse locations with k roll-up, transcript redaction (ARCHITECTURE §7). Raw IPs only in private raw buckets with short retention.

## ADR-004: AWS via Terraform
**Status:** accepted (roadmap and brief)
**Decision:** all infrastructure in Terraform (AWS provider 6.x), remote state in S3 with native lockfile; no click-ops.

## ADR-005: Low-interaction honeypots: Cowrie + OpenCanary
**Status:** accepted for the tools (brief); exact enabled services proposed
**Decision:** Cowrie for SSH/Telnet, OpenCanary for HTTP, FTP, MySQL, Redis.
**Consequences:** attackers see emulated shells; no real OS exposure.

## ADR-006: ML classification of sessions into bots, crypto-miners, humans
**Status:** accepted (roadmap); extra classes `scanner` and `unknown` proposed
**Decision:** weak labels from config-driven labelling functions for training, hand-labelled gold set for evaluation only, LightGBM with a logistic-regression baseline, HDBSCAN clans, ONNX serving.

## ADR-007: Live 3D globe with click-to-replay as the signature UI
**Status:** accepted (roadmap)

## ADR-008: Serverless pipeline (S3, SQS, Lambda, DynamoDB) instead of always-on clusters
**Status:** proposed
**Context:** low volume; budget matters.
**Decision:** S3-triggered Lambdas, DynamoDB on-demand, public JSON on S3 + CloudFront.
**Consequences:** near-zero idle cost; "live" is about two minutes behind.

## ADR-009: Immutable sensors, no SSH, no SSM
**Status:** proposed
**Decision:** no admin path; replace via AMI + Terraform. Avoids SSM interface endpoints (~$22/month/region) and an attack surface.

## ADR-010: Offline enrichment only (DB-IP Lite, Natural Earth)
**Status:** proposed
**Decision:** no runtime third-party lookups about attackers.

## ADR-011: Web stack: Vite + React 19 + TypeScript + three.js (React Three Fiber)
**Status:** proposed
**Context:** Nour's strength is React; the new-stack proof here is cloud, Terraform, security and ML. Keeping React keeps the globe at the "jaw-dropping" bar.

## ADR-012: Python 3.13 managed with uv for pipeline and ML
**Status:** proposed

## ADR-013: Universe events as CloudEvents 1.0 + JSON Schema 2020-12, outbox first
**Status:** accepted for format (matches Darb Budokai ADR-016, itself proposed there); event types proposed
**Decision:** `watchtower.*` events written to an S3 outbox; optional adapter posts to Darb Budokai with HMAC. Integration is a later optional phase.

## ADR-014: Config, not code
**Status:** accepted (hard rule 2)
**Decision:** everything in ARCHITECTURE §11 lives in `config/` validated by JSON Schema.

## ADR-015: UI first
**Status:** accepted (hard rule 3)
**Decision:** design system (Phase 2) and full prototype on demo data (Phase 3) before sensors, pipeline or cloud.

## ADR-016: No AI attribution; Nour is the only author and committer
**Status:** accepted (hard rule 1)
**Decision:** git identity set in repo, commit-msg hook, agent attribution settings off, push checks.

## ADR-017: Ask before paid or public actions; budget alarm before first sensor
**Status:** accepted (hard rules 6 and 9)

## ADR-018: TDD; no real AWS or internet in CI
**Status:** accepted (hard rule 7)
**Decision:** moto, `terraform test` mock providers, sanitised fixtures with documentation-range IPs; CI has no AWS credentials beyond an optional OIDC plan role.

## ADR-019: Native feel on mobile, one modern SVG icon set, no emoji
**Status:** accepted (rule 11)

## ADR-020: Default regions us-east-1, eu-central-1, ap-southeast-1; pipeline in eu-central-1
**Status:** proposed
**Consequences:** about $38/month on-demand for 3 regions; Phase 6 starts with one region.
