# Master plan: 0% to 100%

Each phase is a shippable increment on its own branch, merged into `main` only with Nour's "yes". Weights add to 100%. Progress is tracked in `docs/PROGRESS.md`.

Every phase uses the process skills (`superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:executing-plans`, `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `superpowers:receiving-code-review`, `superpowers:finishing-a-development-branch`, `code-review`, `simplify`). Each phase's "Skills:" line lists the extra ones to invoke before starting.

Paid cloud starts in Phase 6. Phases 0 to 5 cost $0.

| Phase | Name | Weight | Branch |
|---|---|---|---|
| 0 | Repo bootstrap, CI, conventions | 5% | `phase/00-bootstrap` |
| 1 | Spec confirmation with Nour | 4% | `phase/01-spec` |
| 2 | Design system | 10% | `phase/02-design-system` |
| 3 | Globe and screens prototype on seed data | 14% | `phase/03-ui-prototype` |
| 4 | Sensors in the local lab + egress proof | 10% | `phase/04-sensor-lab` |
| 5 | Pipeline: ingest, anonymise, publish (local) | 12% | `phase/05-pipeline` |
| 6 | Terraform + first live region | 12% | `phase/06-first-region` |
| 7 | ML classification and clustering | 12% | `phase/07-ml` |
| 8 | Multi-region, daily stats, clans, outbox | 7% | `phase/08-multi-region` |
| 9 | Darb Budokai integration (optional) | 3% | `phase/09-budokai` |
| 10 | Hardening | 6% | `phase/10-hardening` |
| 11 | Docs, demo GIF, public launch | 5% | `phase/11-launch` |

---

## Phase 0: Repo bootstrap, CI, conventions (5%)

**Goal:** an empty but disciplined monorepo where every later phase can start with a green build.

**Deliverables:** git repo with Nour's identity, folder skeleton (README folder map), `.gitignore`, `.env.example`, `.githooks/commit-msg`, agent settings with attribution off, `Makefile` targets (stubs that fail clearly), Python workspace (uv), web app shell (Vite + React + TS), Terraform skeleton with `envs/bootstrap` and `envs/live`, config schema validation, CI workflow, `ASSETS.md` stub, `LICENSE` (choice in Phase 1; MIT proposed), PR template.

**Tasks (TDD order):**
1. Ask Nour: repo name (`darb-ki` proposed), visibility while building (private proposed), licence. Do not create the remote yet.
2. `git init`, `git config user.name "Nour Alden Mousa"`, `git config user.email "nmcryptoinvest@gmail.com"`, `git config core.hooksPath .githooks`.
3. Write a test script `tests/hooks/test_commit_msg.sh` that expects the hook to reject `Co-Authored-By`, `claude`, `anthropic`, `generated with`; watch it fail; add `.githooks/commit-msg`; watch it pass.
4. `.claude/settings.json` with `"attribution": {"commit": "", "pr": ""}` and `"includeCoAuthoredBy": false`.
5. `make check-emoji` and `make check-private`: write failing tests with sample files containing an emoji and a non-documentation IP; implement the grep scripts.
6. Python: `uv init` workspace with `pipeline` and `ml` packages, ruff, mypy strict, pytest; one trivial test.
7. Web: `npm create vite@latest web -- --template react-ts`; add ESLint, Prettier, Vitest, Playwright + `@axe-core/playwright`; a failing smoke test for an app shell, then the shell.
8. Config: `config/schema/*.json` + a test that validates every YAML in `config/`; seed `config/regions.yaml` etc. with proposed values marked "proposed".
9. Terraform: `infra/envs/bootstrap` (state bucket with versioning + `use_lockfile`), `infra/envs/live` (empty root with backend config), `infra/tests/` with one `terraform test` using `mock_provider "aws"`; verify the AWS provider 6.x per-resource `region` argument works with `for_each` over `config/regions.yaml`.
10. CI (`.github/workflows/ci.yml`): Python lint/type/test, web lint/type/test/e2e, `terraform fmt -check`, `validate`, `test`, tflint, Trivy config, Checkov, `check-emoji`, `check-private`, config schema check. No AWS credentials in CI.
11. PR template (`.github/pull_request_template.md`) with no attribution line.

**Tests that prove it:** `make test` runs all suites green; commit-msg hook test passes; CI green on the branch; a deliberately bad commit message is rejected locally.

**Definition of done:** clean checkout → `uv sync --all-packages && npm --prefix web ci && make test` green; Nour's identity is the only one in `git log`; ledger updated.

**Skills:** `superpowers:using-git-worktrees`, `run`, `security-review` (for the CI and hook setup).

---

## Phase 1: Spec confirmation with Nour (4%)

**Goal:** every open question that blocks design or safety answered and recorded.

**Deliverables:** `docs/specs/YYYY-MM-DD-phase-01-spec.md`, updated `DECISIONS.md` (proposed ADRs accepted or changed), updated `OPEN_QUESTIONS.md` (answered ones moved to an "Answered" section with the date).

**Tasks:**
1. Run `superpowers:brainstorming`. Ask the questions in `docs/OPEN_QUESTIONS.md` **one at a time**, open-ended ones first, in the order listed there.
2. Show the three art directions in `UI_DESIGN.md` §4 as words plus 2–3 reference adjectives each; Nour picks one (still mocks come in Phase 2).
3. Walk Nour through the legal and ethics note (`VISION.md` §6) and the egress table (`ARCHITECTURE.md` §4). Record their explicit acknowledgement in the spec.
4. Confirm cost envelope and budget amount; confirm whether the AWS account has free-plan credits.
5. Write the spec; ask Nour to approve; update `DECISIONS.md`.

**Tests that prove it:** none in code; the spec file exists and is approved (recorded in `PROGRESS.md`).

**Definition of done:** every question marked "Phase 1" in `OPEN_QUESTIONS.md` answered; spec approved; ADR statuses updated.

**Skills:** `superpowers:brainstorming`, `writing-guidelines`.

---

## Phase 2: Design system (10%)

**Goal:** the chosen art direction turned into tokens, type, motion rules, icon set and core components, chosen with Nour side by side.

**Deliverables:** `web/src/design/` tokens as CSS variables (generated from `config/theme/*.yaml`), type scale with chosen Google Fonts, motion tokens (spring presets, durations), icon set chosen (Solar duotone or Lucide) plus custom class glyphs as SVG, core components (Button, IconButton, Tabs, BottomTabBar, Sheet with detents, Chip, Legend, Scrubber, StatTile, Toast, Banner), a `/design` playground route, still mocks and a 10-second motion study for each of the three directions before the pick, `ASSETS.md` filled.

**Tasks (TDD order):**
1. Run `threejs-choose-skills` and record which 3D skills apply to the globe.
2. Produce the three direction studies (still + short motion) on a bare globe with demo arcs; Nour picks; record in `DECISIONS.md`.
3. Contrast test first: a Vitest test that loads token pairs and asserts WCAG AA ratios; watch it fail on placeholder tokens; set real tokens.
4. Reduced-motion test first: a hook `useMotionPreference` test; implement.
5. Each component: Testing Library test (role, name, keyboard behaviour, pressed state) → component → playground entry. Sheet: drag-to-dismiss and detents, with keyboard equivalents.
6. Emoji/icon lint: ESLint rule or test that forbids emoji literals and non-approved icon imports.
7. Axe run on `/design`.
8. Show Nour the playground side by side with the mocks; record approval.

**Tests that prove it:** contrast test, component tests, axe zero serious/critical on `/design`, `check-emoji` green.

**Definition of done:** Nour approved tokens, type, icons and components (recorded); no hardcoded colours or copy in components.

**Skills:** `frontend-design`, `impeccable:impeccable`, `design-taste-frontend`, `build-awwwards-quality-sites`, `design-first-ui-prompting`, `design:design-system`, `design:design-critique`, `design:accessibility-review`, `audit-reference-originality`, `solar-duotone-bold`, `company-logos`, `animation-systems`, `threejs-choose-skills`, `3dviz-pro-max`, `threejs-procedural-materials`, `react-best-practices`, `composition-patterns`.

---

## Phase 3: Globe and screens prototype on seed data (14%)

**Goal:** the full clickable product on demo data, approved by Nour screen by screen, before any backend work.

**Deliverables:** demo seed (`config/seed/demo/`: ~500 synthetic sessions across classes, documentation-range IPs only, realistic timings, already redacted), `DemoFeed`, event scheduler, the globe with beacons/arcs/rings per class, replay sheet/panel, Today, Clans, Model, Method screens, private Labelling and Watchtower Status screens (local only), all states (§2.9 of UI_DESIGN), 2D fallback map, reduced-motion paths, mobile layouts with native feel.

**Tasks (TDD order):**
1. Seed generator script (`tools/seed/`) with tests: deterministic from a seed number, every IP in documentation ranges, every class present, timings plausible per class (parameters in config).
2. Scheduler: tests for mapping timestamps to render times, burst batching with cap and "+N more" counter, pause/resume; then implement.
3. `FeedSource` interface + `DemoFeed`: tests then implement.
4. Globe scene: land shader, beacons, arcs per class (instanced), camera rig with damping and auto-rotate rules; visual tests with `toHaveScreenshot` at a fixed seed; performance check (`performance-profiling`).
5. Latest-sessions list (accessible equivalent): tests for keyboard and `aria-live` rate limiting; implement.
6. Replay: tests for keystroke timing, speed control, skip idle, redaction tokens rendered as text (XSS/ANSI fuzz strings), reduced-motion line mode; implement panel (desktop) and sheet (mobile).
7. Today (charts), Clans (constellation), Model (model card from a demo JSON), Method (seven-layer diagram): each with a test of content from config, then build.
8. Labelling and Watchtower Status (local-only routes, hidden in production build): tests that they are excluded from the production bundle.
9. States: empty, loading, error, offline, WebGL unavailable (2D fallback), Demo banner.
10. Playwright e2e for every screen: keyboard path, reduced motion, 360px and desktop; axe.
11. Screen-by-screen review with Nour: screenshot + two lines each; record verdicts; iterate.

**Tests that prove it:** Vitest suites green, Playwright e2e + axe green, visual snapshots stable, 60 fps target measured on Nour's laptop (recorded), `check-emoji` green.

**Definition of done:** every screen approved by Nour in the ledger; demo mode labelled; no copy or thresholds hardcoded.

**Skills:** `frontend-design`, `impeccable:impeccable`, `design-taste-frontend`, `build-awwwards-quality-sites`, `ui-implementer`, `web-design-guidelines`, `design:design-critique`, `design:accessibility-review`, `design:ux-copy`, `design:design-handoff`, `threejs`, `threejs-web-design`, `3dviz-pro-max`, `globe-gl`, `globe-particles`, `threejs-bloom`, `threejs-camera-controls-and-rigs`, `threejs-particles-trails-and-effects`, `threejs-procedural-geometry`, `threejs-exposure-color-grading`, `threejs-compatibility-fallbacks`, `threejs-debugging`, `threejs-visual-validation`, `add-mouse-driven-orbit`, `animation-systems`, `gsap`, `optimize-web-animations`, `dataviz`, `react-best-practices`, `composition-patterns`, `performance-profiling`, `playwright-cli`, `run`, `procedural-sfx` (only if Nour wants sound).

---

## Phase 4: Sensors in the local lab + egress proof (10%)

**Goal:** Cowrie and OpenCanary running locally with the production config, provably unable to reach outward, producing real logs from replayed attacks.

**Deliverables:** `sensor/` configs rendered from `config/personas/*.yaml`, Cowrie command stubs (wget/curl/tftp/ftpget), file hash-and-delete unit, nftables ruleset, Vector config, Packer template (not built yet), `lab/compose.yml`, attack replayer with sanitised recorded sessions, `outside` container, `make lab-up lab-attack lab-egress-check`.

**Tasks (TDD order):**
1. `test_cowrie_config.py`: forwarding off, only `jsonlog` output, stubs registered, download size limit from config. Fail, then render config from templates.
2. Command stub tests: invoking `wget http://example.invalid/x` logs the URL, prints a DNS failure, opens no socket (assert with a socket monkeypatch). Implement stubs.
3. Hash-and-delete tests: a file dropped in the downloads dir is recorded as `{sha256,size}` and removed within the configured time. Implement systemd path unit + script.
4. nftables tests in a privileged container: `cowrie` uid cannot connect out; `vector` uid only TCP 443 and DNS to the resolver address; drops are counted. Implement ruleset.
5. Lab egress check: tests that every probe from sensor containers to `outside` fails. Implement `lab/egress-check`.
6. Replayer: tests for timing fidelity on a recorded session; implement with asyncssh.
7. Vector config: test that output lands in moto S3 with the right prefix and fields; implement.
8. Packer template: `packer validate` in CI; HCL variables from config; build only in Phase 6.

**Tests that prove it:** all of the above green in CI (privileged job for nftables), `make lab-up lab-attack` shows sessions in moto S3, `make lab-egress-check` reports every probe blocked.

**Definition of done:** a replayed attack produces Cowrie logs in moto S3; no sensor container can reach `outside`; `security-review` run on `sensor/` with findings fixed.

**Skills:** `security-review`, `superpowers:systematic-debugging`, `run`.

---

## Phase 5: Pipeline: ingest, anonymise, publish (local) (12%)

**Goal:** logs from the lab become redacted, pseudonymised, published sessions that the real UI plays, all on moto, with a placeholder classifier.

**Deliverables:** `pipeline/` core (parsers, `Session` model, GeoIP enrichment with DB-IP Lite, pseudonymiser, codenames, coarse location with k roll-up, redactor), Lambda handlers `ingest`, `classify` (rule-based placeholder from `config/labelling/`), `publish`, `LabFeed` in the web app, `make geoip-update`.

**Tasks (TDD order):**
1. Parser tests on recorded, sanitised Cowrie and OpenCanary logs (fixtures with documentation IPs); implement parsers into `Session`.
2. Pseudonymiser tests: keyed, stable within a key period, different across periods, never returns the IP; implement.
3. Redactor property tests (hypothesis): no IPv4/IPv6/URL/email/wallet survives; control and escape sequences stripped; public-credential allowlist respected; implement from `config/redaction/rules.yaml`.
4. Coarse location tests: snapping to centroid, k roll-up to country; implement with Natural Earth data.
5. Handler integration tests on moto: S3 event → SQS → ingest → DynamoDB (assert no IP attribute anywhere) → classify → publish → public bucket objects match JSON Schemas in `contracts/public/`.
6. Public feed schema tests; the web `LabFeed` consumes them (contract test shared between Python and TS via the JSON Schemas).
7. End-to-end lab test: `make lab-attack` → session visible in the UI in lab mode within the configured delay.

**Tests that prove it:** pytest suites green; the lab e2e passes; `check-private` scans the public bucket output and finds no IP.

**Definition of done:** UI in lab mode replays a real (lab) attack, redacted; no raw IP outside raw storage; `security-review` on `pipeline/` done.

**Skills:** `security-review`, `superpowers:subagent-driven-development` (parsers, redactor and handlers are independent tasks), `run`, `playwright-cli`.

---

## Phase 6: Terraform + first live region (12%)

**Goal:** one real region live on AWS, attacks arriving, egress proven in the real cloud. **First paid phase. Ask Nour before `apply`.**

**Deliverables:** modules `sensor-region`, `pipeline`, `public-site`, `budget`; `infra/envs/live` wiring from config; Packer AMI build; OIDC role for CI plan; Infracost report; `make plan apply teardown kill-sensors cloud-inventory`; `scripts/deregister-amis.sh`, `scripts/leftover-check.sh`; tripwire Lambda.

**Tasks (TDD order):**
1. `egress.tftest.hcl` first (all assertions in ARCHITECTURE §4), watch it fail, then write `sensor-region`.
2. Tests for buckets (private, encrypted, Block Public Access, lifecycle from config, `force_destroy` from config), IAM (only PutObject on own prefix), endpoint policy; implement.
3. Tripwire tests (moto + recorded flow log lines): SYN-only egress not to S3 triggers SNS + quarantine + stop; normal reply traffic does not; implement.
4. Budget module test (exists, threshold from config); implement.
5. `public-site` tests: OAC, no public bucket policy, CSP header present; implement.
6. `make plan` with Infracost; paste cost into the ledger; **ask Nour** with the plan summary and cost.
7. After "yes": bootstrap state, build AMI with Packer in the build VPC, `apply` one region (`eu-central-1` proposed) + pipeline + site + budget.
8. Real egress probe (test AMI variant) → all blocked; 24 h of flow logs with zero tripwire hits; first real attack recorded and visible on the site (site stays unlisted until launch).
9. Rehearse `make kill-sensors` and `make teardown` + re-apply once, so teardown is proven (ask Nour first).

**Tests that prove it:** `terraform test` green; Checkov/Trivy clean or justified; real egress probe report; tripwire unit tests; teardown leftover check prints nothing.

**Definition of done:** one region live within budget, egress proven, teardown proven, cost table updated with real numbers.

**Skills:** `security-review`, `superpowers:verification-before-completion`, `superpowers:systematic-debugging`.

---

## Phase 7: ML classification and clustering (12%)

**Goal:** an honest classifier (bot, miner, human, plus scanner and unknown if confirmed) and attacker clans, served in the pipeline via ONNX, with a published model card.

**Deliverables:** `ml/` features (shared with pipeline), weak-labelling functions in config, gold set from the Labelling screen (Nour labels; size agreed in Phase 1), training scripts (baseline logistic regression, LightGBM), temporal split evaluation, HDBSCAN clans over command-sequence TF-IDF + HASSH + timing features, ONNX export, model card JSON + Markdown, `config/model.yaml` promotion flow, Model screen and Clans screen on real data.

**Tasks (TDD order):**
1. Feature tests (deterministic, no IP-derived features, handles empty sessions); implement.
2. Labelling-function tests on hand-made fixtures; implement from `config/labelling/*.yaml`.
3. `make ml-export`: test that exported training data contains no IPs and no raw credentials; implement (from DynamoDB via Nour's SSO role, into `data/private/`).
4. Nour labels the gold set using the Labelling screen (time-boxed; record count).
5. Training + eval tests: temporal split has no overlap; metrics computed on gold set only; report regenerates; implement.
6. ONNX parity test: ONNX output matches the native model within tolerance; implement export.
7. Classify Lambda swaps the placeholder for ONNX behind `config/model.yaml`; integration test on moto.
8. Clustering: stability test across seeds; implement; clan labels written by the aggregate job.
9. Model card generated from the eval report (no hand-typed numbers); Model screen reads it.
10. Ask Nour to promote the model; emit `watchtower.model.promoted` to the outbox.

**Tests that prove it:** pytest ML suite; ONNX parity; eval report checked in (numbers only, no data); Model screen e2e.

**Definition of done:** model live in the pipeline, card published with real held-out metrics and failure modes, Nour approved promotion.

**Skills:** `dataviz`, `superpowers:subagent-driven-development`, `superpowers:systematic-debugging`.

---

## Phase 8: Multi-region, daily stats, clans, outbox (7%)

**Goal:** all configured regions live, nightly aggregates and the universe outbox running. **Ask Nour before adding regions (cost).**

**Deliverables:** regions 2 and 3 from config, S3 replication from each, aggregate Lambda (daily stats, k roll-up, clans), event schemas in `contracts/events/` with examples, outbox writer, Today screen on real data.

**Tasks (TDD order):**
1. Terraform tests for N regions from config (each has the full egress assertion set); implement `for_each`.
2. Aggregate tests on moto (counts, k-anonymity roll-up, timezone boundaries from config); implement.
3. Schema tests (valid/invalid examples) for the four `watchtower.*` events; write schemas.
4. Outbox writer tests (idempotent UUIDv5 ids, no private fields); implement.
5. Plan + Infracost; **ask Nour**; apply.
6. 48 hours of all regions with zero tripwire hits; cost check vs table.

**Tests that prove it:** terraform tests; aggregate and outbox tests; real multi-region egress probe report.

**Definition of done:** all regions live within budget, daily stats visible, outbox filling.

**Skills:** `security-review`, `dataviz`, `superpowers:verification-before-completion`.

---

## Phase 9: Darb Budokai integration (optional) (3%)

**Goal:** `watchtower.*` events reach Darb Budokai's ingest, if Nour wants it and Darb Budokai runs.

**Deliverables:** `adapters/budokai/` with HMAC signing and batching, fake-ingest tests, a PR in Darb Budokai's repo adding the contracts (ask Nour), local end-to-end run against Darb Budokai's compose stack.

**Tasks:** see `INTEGRATION.md` §7, each step test-first (signature format, batching, retry, idempotency).

**Tests that prove it:** adapter tests against `pytest-httpserver`; local e2e against Darb Budokai.

**Definition of done:** Nour sees the nightly siege in Darb Budokai's battle log, or Nour defers this phase (record the ruling; weight then moves to Phase 10).

**Skills:** `security-review`, `superpowers:test-driven-development`.

---

## Phase 10: Hardening (6%)

**Goal:** safe to leave running and safe to show publicly.

**Deliverables:** threat model document (`docs/THREAT_MODEL.md`: sensor compromise, pipeline poisoning, XSS via transcripts, cost attacks, abuse reports), fuzz tests for parsers and redaction, CSP and headers verified, rate limiting on CloudFront if needed, alarm on pipeline DLQ depth, key rotation runbook, spot option evaluated (Nour decides), Lighthouse and performance pass, accessibility audit, chaos check (kill a sensor, see status and recovery), retention verified (objects older than retention are gone).

**Tasks (TDD order):** each risk gets a failing test or check first (fuzz corpus, header test, DLQ alarm test in terraform test, retention test on moto), then the fix.

**Tests that prove it:** fuzz suite, Lighthouse ≥ 85 mobile, axe clean, terraform tests, a full `security-review` and `code-review` pass with findings fixed.

**Definition of done:** threat model reviewed by Nour; no open high findings.

**Skills:** `security-review`, `code-review`, `simplify`, `performance-profiling`, `optimize-web-animations`, `optimize-threejs-games`, `threejs-compatibility-fallbacks`, `design:accessibility-review`, `web-design-guidelines`.

---

## Phase 11: Docs, demo GIF, public launch (5%)

**Goal:** a public repo and site that explain themselves in 10 seconds and hold up under a security interviewer's questions. **Ask Nour before making anything public.**

**Deliverables:** README (hero GIF, what it is, architecture diagram, egress table summary, cost, teardown, ethics link, "built with" strip using Simple Icons), demo GIF recorded in demo mode or with fully redacted live data (no IPs, checked frame by frame), Method page final, Darb Kaioken write-up outline handed to Darb Kaioken, public repo and site (after "yes").

**Tasks:**
1. README and docs pass; run `writing-guidelines`.
2. Record the GIF (browser recording); review every frame for IPs and URLs; `check-private` on any text in it.
3. Final `check-emoji`, `check-private`, push checklist (CLAUDE.md §7).
4. **Ask Nour**: make the repo public, publish the site, share.
5. After "yes": `publish-project-to-github`, deploy, verify live site.

**Tests that prove it:** all suites green on `main`; push checks pass; live site smoke test.

**Definition of done:** public repo with only Nour as contributor, live site, README complete.

**Skills:** `publish-project-to-github` (only after Nour's yes), `writing-guidelines`, `design:ux-copy`, `browser-video-recording`, `company-logos`, `audit-reference-originality`, `superpowers:finishing-a-development-branch`.
