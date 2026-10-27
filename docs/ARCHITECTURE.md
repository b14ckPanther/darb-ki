# Architecture

Status: AWS + Terraform, low-interaction honeypots, multi-region, ML classification (bots, crypto-miners, humans), live 3D globe with session replay and Darb Budokai "invaders" come from Nour's roadmap. Everything else here (exact AWS services, regions, libraries, names) is **proposed, confirm with Nour in Phase 1**, except the safety rules in §4, §7 and §8, which are fixed.

## 1. Shape in one paragraph

Small, immutable EC2 sensors in several AWS regions run **Cowrie** (SSH/Telnet) and **OpenCanary** (HTTP, FTP, MySQL, Redis). They accept inbound connections from anyone but **cannot start outbound connections**, except Vector shipping logs over HTTPS to a same-region S3 gateway endpoint locked to one bucket. Regional raw buckets replicate into a central private bucket. S3 events drive a chain of Python Lambdas: **ingest** (parse, normalise, offline GeoIP, pseudonymise), **classify** (ONNX model: bot, miner, human, scanner, unknown), **publish** (redacted public JSON to a CloudFront-served bucket). The React + Three.js globe polls that public feed and plays events about two minutes behind real time. A **tripwire** Lambda watches VPC flow logs and quarantines any sensor that ever initiates an outbound connection. A nightly **aggregate** Lambda builds daily stats and the universe events for Darb Budokai.

## 2. Diagram

```
  Internet attackers
        │  inbound only (22, 23, 80, 21, 3306, 6379 from config)
        ▼
┌──────────────────────── sensor region (x N, from config/regions.yaml) ──────────────────────┐
│ VPC 10.x.0.0/24, one public subnet, IGW, NO NAT, IPv6 off                                    │
│  ┌───────────────────────────── EC2 t4g.micro (immutable AMI, no SSH, no SSM) ───────────┐  │
│  │ Cowrie :2222/:2223 (nft redirect 22/23)  OpenCanary :80 :21 :3306 :6379                 │  │
│  │      │ json logs + ttylogs                    │ json logs                               │  │
│  │      └──────────────► Vector (uid vector) ◄───┘   uploads hashed+deleted, never shipped │  │
│  │ nftables: output policy DROP; only uid vector → 443 S3, 53 VPC resolver; IMDS for vector │  │
│  └────────────────────────────┬───────────────────────────────────────────────────────────┘  │
│  SG egress: 443 → S3 prefix list only     NACL: outbound only 443 + ephemeral replies         │
│                               ▼                                                               │
│                S3 gateway endpoint (policy: PutObject to ki-raw-<region> only)               │
│                               ▼                                                               │
│                s3://ki-raw-<region>  (private, SSE-S3, lifecycle 30 d)                       │
│  VPC flow logs → s3://ki-flowlogs (central) ─────────────────────────┐                       │
└───────────────────────────────┬───────────────────────────────────────┼───────────────────────┘
                                │ S3 replication                         │
                                ▼                                        ▼
┌──────────────────────── pipeline region (eu-central-1 proposed) ─────────────────────────────┐
│ s3://ki-raw-central ──event──► SQS ingest ──► λ ingest ──► SQS classify ──► λ classify       │
│                                   (DLQ)        parse, normalise,      ONNX model v from config │
│                                                GeoIP (DB-IP Lite),          │                  │
│                                                pseudonymise, redact          ▼                 │
│                                                       DynamoDB ki-sessions (pseudonymised)   │
│                                                                      │ stream                 │
│                                                                      ▼                        │
│ EventBridge Scheduler ──► λ aggregate (nightly)           λ publish (redacted, coarse geo)    │
│        daily stats, universe events → outbox/                        │                        │
│ λ tripwire ◄── flow logs: sensor-initiated SYN not to S3 → SNS email + quarantine SG + stop  │
│ AWS Budget alarm → SNS email                                         ▼                        │
│                                         s3://ki-public ──► CloudFront (OAC, strict CSP)      │
└──────────────────────────────────────────────────────────────────────┼────────────────────────┘
                                                                       ▼
                                  web: Vite + React + Three.js globe (polls live/latest.json)
                                  optional: budokai adapter reads outbox/ → Darb Budokai ingest (later)
```

## 3. Components

| Component | Tech | Responsibility |
|---|---|---|
| `sensor/` | Cowrie 2.x, OpenCanary 0.9.x, Vector 0.4x, nftables, Packer 1.x, Amazon Linux 2023 arm64 | Decoy services, persona from `config/personas/*.yaml` (hostname, banner, fake filesystem, fake users), log shipping. AMI built by Packer in a separate build VPC with internet, never in the sensor VPC. |
| `infra/modules/sensor-region` | Terraform, AWS provider 6.x | VPC, subnet, IGW, route table, S3 gateway endpoint + policy, SG, NACL, EIP, instance (IMDSv2, hop limit 1), IAM role (PutObject on own prefix only), flow logs, raw bucket + replication. One instance per region in `config/regions.yaml`. |
| `infra/modules/pipeline` | Terraform | Central buckets, SQS queues + DLQs, Lambdas, DynamoDB, EventBridge Scheduler, SNS topic, tripwire, quarantine SG per region. |
| `infra/modules/public-site` | Terraform | Public bucket, CloudFront with Origin Access Control, response headers policy (CSP, HSTS), optional custom domain. |
| `infra/modules/budget` | Terraform | AWS Budget with forecast alerts from `config/budget.yaml`. |
| `pipeline/` | Python 3.13, Pydantic 2, boto3, onnxruntime, `maxminddb` reader for DB-IP Lite mmdb | Lambda handlers + pure core library (parsers, normaliser, redactor, pseudonymiser, feature extractor). Handlers are thin. |
| `ml/` | pandas, scikit-learn, LightGBM, HDBSCAN (`sklearn.cluster.HDBSCAN`), skl2onnx / onnxmltools, matplotlib | Feature definitions shared with `pipeline/` (one package), weak labelling, training, evaluation, model card generation, ONNX export. Runs on Nour's laptop. No SageMaker. |
| `web/` | Vite 7, React 19, TypeScript, three.js, @react-three/fiber 9, @react-three/drei, three-globe, Zustand, GSAP (UI motion) | Globe, replay, stats, method page. Reads only the public feed. Pin exact current versions in Phase 0. |
| `lab/` | Docker Compose, moto_server | Full local stack on an `internal: true` Docker network, attack replayer, egress checker. |
| `adapters/budokai/` | Python | Optional later: reads `outbox/` events, signs and posts them to Darb Budokai ingest (`docs/INTEGRATION.md`). |

### Why Lambda + DynamoDB + S3, not Kafka/Elasticsearch/ECS

Volume is small (thousands of sessions a day). Serverless pieces cost near zero inside the free tier, need no patching, and Terraform covers them fully. A always-on OpenSearch or ECS cluster would cost more than the sensors. ADR-008.

## 4. Egress rules (fixed: sensors must never attack outward)

The rule: **a sensor may answer connections that attackers open. It may never open a connection of its own, except Vector to S3 in its own region.** Seven independent layers enforce it, so one mistake cannot break it.

**Important nuance:** AWS security groups are stateful. Replies to an inbound attacker connection are allowed automatically. That is how the honeypot talks back. What is blocked is any **new** outbound connection.

| # | Layer | Rule | What it stops |
|---|---|---|---|
| 1 | **Routing** | No NAT gateway. No egress-only IGW. IPv6 disabled on VPC and subnet. Route table: `0.0.0.0/0 → IGW` (needed so inbound works with a public IP) and S3 prefix list → gateway endpoint. | IPv6 side channels; private-subnet tricks. |
| 2 | **Security group** `ki-sensor` | Ingress: honeypot ports from `config/regions.yaml` (`22, 23, 80, 21, 3306, 6379` proposed) from `0.0.0.0/0`. **Egress: exactly one rule: TCP 443 to the region's S3 managed prefix list** (`com.amazonaws.<region>.s3`). The default allow-all egress rule is removed (Terraform `aws_vpc_security_group_egress_rule`, no inline default). | Any new outbound TCP/UDP/ICMP to the internet. |
| 3 | **Network ACL** (stateless) | Outbound allow: TCP dst `1024-65535` (replies to attacker ephemeral ports), TCP dst `443`. Outbound deny all else. Inbound allow honeypot ports and TCP `1024-65535` (S3 replies). | Even if layer 2 were wrong: no outbound SSH, Telnet, SMTP (25), HTTP (80), SMB (445), RDP, DNS to the internet, or UDP floods. |
| 4 | **Host firewall** nftables (baked into AMI) | `output` chain policy `drop`. Allow `ct state established,related`. Allow new connections **only** for `meta skuid vector` to TCP 443, and to UDP/TCP 53 at the VPC resolver (`169.254.169.253`). Allow `skuid vector` to IMDS `169.254.169.254:80` (credentials). Allow `chronyd` to `169.254.169.123` (Amazon Time Sync). Every dropped packet is counted and logged with prefix `HPG-EGRESS-DROP`. | The honeypot processes (`cowrie`, `opencanary` users) can never open a socket outward, whatever the cloud config says. |
| 5 | **Application config** | Cowrie: `[ssh] forwarding = false`, `forward_redirect = false`, `forward_tunnel = false`; the `wget`, `curl`, `tftp`, `ftpget` command modules replaced by stubs that log the URL and print a realistic DNS failure (verify module names against the pinned Cowrie version in Phase 4); `download_limit_size` small (from config); every output plugin other than `jsonlog` disabled (no VirusTotal, no external DBs). OpenCanary: only listed modules enabled. | Honeypot features that would fetch from or relay to the internet. |
| 6 | **IAM + endpoint policy** | Instance role: `s3:PutObject` on `arn:aws:s3:::ki-raw-<region>/sensor=<id>/*` only. S3 gateway endpoint policy: allow `s3:PutObject` to that bucket only. No other AWS API. No SSM agent, no SSH key, no EC2 Instance Connect. | Exfiltration to an attacker-controlled S3 bucket; lateral moves with stolen instance credentials. |
| 7 | **Detection + kill switch** | VPC flow logs (v5 fields incl. `tcp-flags`, `flow-direction`) go to the central bucket. The `tripwire` Lambda flags any flow where `srcaddr` is a sensor, `flow-direction = egress`, `tcp-flags` has SYN without ACK, and the destination is not in the S3 prefix list. On a hit: SNS email to Nour, swap the instance to the empty `ki-quarantine` SG, stop the instance. The nftables drop counter (shipped by Vector) is a second signal. | Anything the first six layers somehow missed, plus config drift. |

**Admin access:** none. Sensors are immutable. To change one, rebuild the AMI and replace the instance with Terraform. Debug from shipped logs only. This removes SSH as an attack surface and removes the need for SSM interface endpoints (which would cost about $22/month per region).

**Tests that prove the rules** (written before the infra, in TDD order):
- `infra/tests/egress.tftest.hcl` (mock provider): sensor SG has exactly one egress rule, port 443, destination is the S3 prefix list; NACL outbound rules match the table above; no NAT gateway, no egress-only IGW, IPv6 off; IAM policy has only `s3:PutObject` on the own prefix; endpoint policy restricts to the own bucket.
- `sensor/tests/test_nftables.py`: `nft -c -f` validates the ruleset; in a privileged test container with network namespaces, a process running as `cowrie` cannot connect out, `vector` can reach only 443.
- `sensor/tests/test_cowrie_config.py`: forwarding off, stub commands registered, only `jsonlog` output enabled.
- `make lab-egress-check`: from inside the lab sensors, attempt TCP 22/25/80/443/445 and UDP 53/123 to an "outside" container on another network. Every attempt must fail.
- Phase 6, real account (after Nour's "yes"): run `sensor-egress-probe` (a one-off SSM-free check baked into a test AMI variant) that tries the same connections from a real sensor and reports to S3. Expected: all blocked. Plus 24 hours of flow logs with zero tripwire hits.
- Checkov and tfsec-equivalent Trivy rules run in CI on every `infra/` change.

## 5. Data flow, step by step

1. Attacker connects to a sensor. Cowrie writes `cowrie.json` events (`session.connect`, `login.failed`, `login.success`, `command.input`, `session.file_upload`, `client.version`, `client.kex` with HASSH, `session.closed`) and a ttylog per session (keystrokes with timing). OpenCanary writes JSON events per module.
2. Files attackers upload or try to download: Cowrie already names them by SHA-256. A systemd path unit on the sensor records `{sha256, size}` and deletes the file within seconds. File content never reaches Vector.
3. Vector (uid `vector`) tails logs, adds `sensor_id`, `region`, `persona`, batches (60 s or 5 MB, from config), gzips, writes `s3://ki-raw-<region>/sensor=<id>/date=YYYY-MM-DD/<ts>.json.gz`.
4. S3 replication copies raw objects to `ki-raw-central`. Both buckets: private, SSE-S3, Block Public Access, lifecycle delete after `retention.raw_days` (30 proposed).
5. `ObjectCreated` → SQS `ki-ingest` → **λ ingest**: parse both formats into one `Session` model (Pydantic), attach offline GeoIP + ASN (DB-IP Lite mmdb in a Lambda layer, refreshed monthly by Nour with `make geoip-update`), compute the public pseudonym and coarse location (§7), redact the transcript (§7), store in DynamoDB `ki-sessions`. **The raw IP is not written to DynamoDB.** It exists only in the raw buckets.
6. **λ classify** (SQS `ki-classify`): features → ONNX model (version from `config/model.yaml`) → `class`, `confidence`, `evidence` (feature-based reason chips, templates in `config/copy/en/evidence.yaml`). Below the confidence threshold in config → `unknown`.
7. DynamoDB stream → **λ publish**: writes `live/latest.json` (rolling window, size from config), `sessions/<sessionPseudoId>.json` (redacted replay: events with relative timings), and updates `stats/today.json`. CloudFront caches `live/` for a few seconds (TTL from config), everything else longer.
8. **λ aggregate** (EventBridge Scheduler, nightly, timezone from config): `stats/daily/<date>.json`, cluster labels refresh, universe events to `s3://ki-raw-central/outbox/<date>/` (`docs/INTEGRATION.md`).
9. The web app polls `live/latest.json` (interval from config, 15 s proposed) and schedules each event onto the globe at its real relative time, so the globe plays smoothly about two minutes behind reality. The UI says so: "live, about 2 minutes behind".

## 6. Enrichment rules

- Offline only. No lookups that touch attacker infrastructure or third-party APIs at runtime: no reverse DNS, WHOIS, Shodan, AbuseIPDB, VirusTotal.
- GeoIP: DB-IP "IP to City Lite" and "IP to ASN Lite" (CC BY 4.0, attribution required in the UI footer). MaxMind GeoLite2 is the alternative if Nour prefers (needs a free account and licence key).
- Coastlines and city centroids: Natural Earth (public domain).

## 7. Anonymisation and redaction (fixed: no attacker IP in public views)

| Data | Raw bucket (private) | DynamoDB (private) | Public feed and site |
|---|---|---|---|
| Attacker IP | yes, deleted after `retention.raw_days` | **no** | **never** |
| Attacker identity | IP | pseudonym | codename from pseudonym, e.g. "Slate Heron" (word lists in `config/codenames.yaml`) |
| Location | GeoIP point | city + country | snapped to city centroid (Natural Earth places above a population threshold in config) else country centroid. Cities with fewer than `k` sessions that day (3 proposed) roll up to country. |
| ASN | number + org | number + org | org name only (e.g. a hosting provider), proposed; confirm with Nour |
| Credentials tried | full | full | usernames and passwords shown only if on the public default-credentials list in `config/redaction/public-credentials.txt`; others become `[password]` |
| Typed commands | full | redacted | redacted: IPv4/IPv6 → `[ip]`, URLs and domains → `[url]`, emails → `[email]`, crypto wallet addresses → `[wallet]`, base64/hex blobs over N chars → `[blob 2.1 KB]`, control and escape sequences stripped. Patterns in `config/redaction/rules.yaml`. |
| Files | SHA-256 + size only | same | SHA-256 + size, no link, no content |
| Sensor IP | yes | no | **never**; only the region label |

**Pseudonym:** `HMAC-SHA256(key, ip)` → first 40 bits → codename. A keyed hash is required because the IPv4 space is small enough to reverse an unkeyed hash by brute force. The key lives in SSM (SecureString) and rotates on the schedule in config (monthly proposed), which also stops long-term linking.

**Rendering safety:** attacker input is untrusted. The web app renders transcripts as plain text in its own replay component (no `innerHTML`, no terminal emulator that interprets escape sequences). CloudFront sends a strict CSP. Fuzz tests feed known XSS and ANSI/OSC payloads through redaction and rendering.

## 8. Malware policy (fixed)

- Never store file content outside the sensor's temporary download directory, and delete it within seconds of hashing.
- Never upload content or hashes to third-party services from the pipeline. Nour may look up a hash manually in a browser.
- Never publish samples, download links, or full payload URLs (URLs are redacted to `[url]`; the domain is not shown).
- Repo has a CI check (`make check-private`) that fails on non-documentation IPs, on URLs inside fixture transcripts, and on any binary file under `pipeline/tests/fixtures/`.

## 9. Cost (monthly estimate, October 2026 on-demand prices, verify with Infracost in Phase 6)

Assumptions: 3 sensor regions (`us-east-1`, `eu-central-1`, `ap-southeast-1`, proposed), pipeline in `eu-central-1`, 1–3 GB of flow logs per region, a few GB of logs, light public traffic.

| Item | Unit price | 1 region | 3 regions |
|---|---|---|---|
| EC2 `t4g.micro` on-demand, 730 h | $0.0084–0.0106/h by region | $6.13 | $20.90 |
| Public IPv4 address (EIP) | $0.005/h | $3.65 | $10.95 |
| EBS gp3 8 GiB | $0.08–0.096/GB-month | $0.64 | $2.10 |
| VPC flow logs delivered to S3 | $0.25/GB | $0.50 | $1.50 |
| S3 PUTs (Vector every 60 s) + replication + storage | | $0.40 | $1.30 |
| Lambda, SQS, DynamoDB on-demand, SNS, EventBridge, CloudFront | free tier at this volume | $0–1 | $0–1 |
| CloudWatch Logs (Lambda logs, 7-day retention) | $0.50/GB ingested | $0.50 | $0.50 |
| AWS Budgets (2 budgets) | free | $0 | $0 |
| Data transfer out | first 100 GB/month free | $0 | $0 |
| Packer AMI builds | ~$0.05 per build | ~$0.10 | ~$0.30 |
| **Total** | | **≈ $12** | **≈ $38** |

Options:
- **Spot instances** for sensors (honeypots tolerate interruptions): EC2 drops to roughly $2 per region, total ≈ **$23** for 3 regions. Proposed as a Phase 10 option.
- **Not used on purpose:** NAT gateway (~$33/month per region, and it would give sensors egress), SSM interface endpoints (~$22/month per region), GuardDuty, OpenSearch, KMS customer keys ($1/key).
- **Free plan credits:** AWS accounts created after July 15, 2025 get a credit-based free plan. If Nour's account has credits, they cover early months. Check in Phase 1.
- Optional custom domain on `zangeel.dev`: a CNAME at the existing DNS provider costs nothing extra; a Route 53 hosted zone would add $0.50.

Budget guard: AWS Budget at the amount in `config/budget.yaml` ($40 proposed), email alerts at 50%, 80% and 100% of forecast. `make cloud-inventory` prints month-to-date spend (Cost Explorer API, $0.01 per request).

Local development (Phases 0 to 5) costs **$0**.

## 10. Teardown

One command, after Nour's "yes":

```bash
make teardown
```

It runs, in order:

```bash
terraform -chdir=infra/envs/live destroy            # all sensors, pipeline, public site, budget (asks for "yes")
scripts/deregister-amis.sh                           # Packer AMIs + their EBS snapshots, all configured regions (not in TF state)
scripts/leftover-check.sh                            # aws resourcegroupstaggingapi get-resources --tag-filters Key=project,Values=darb-ki
                                                     #   for every region in config/regions.yaml; must print nothing
```

Raw, flow-log and public buckets have `force_destroy` set from config so `destroy` can empty them. The state bucket created by `infra/envs/bootstrap` survives on purpose (cost: cents). To remove that too: `make teardown-all` (empties the versioned state bucket, then `terraform -chdir=infra/envs/bootstrap destroy`).

**Emergency stop** (abuse report, tripwire, unexpected bill): `make kill-sensors` runs `aws ec2 stop-instances` on every instance tagged `project=darb-ki,role=sensor` in every configured region. No Terraform needed. Then investigate.

## 11. Config, not code

```
config/
├── regions.yaml            sensor regions, instance type, spot on/off, ports per region
├── personas/*.yaml         hostname, banners, fake filesystem seed, fake users per persona
├── budget.yaml             monthly limit, alert thresholds, emails (address from env)
├── retention.yaml          raw_days, sessions_ttl_days, flowlog_days
├── pipeline.yaml           batch sizes, live window size, cache TTLs, poll interval
├── model.yaml              active model version, confidence threshold, class list
├── labelling/*.yaml        weak-labelling functions (regex, thresholds, weights)
├── features.yaml           feature list and parameters
├── redaction/rules.yaml    redaction patterns; public-credentials.txt
├── codenames.yaml          word lists for codenames
├── anonymity.yaml          k for roll-up, population threshold for city snapping, key rotation
├── copy/en/*.yaml          all UI copy, evidence chip templates, class descriptions
├── theme/*.yaml            arc colours per class, globe settings (picked in Phase 2)
└── seed/demo/*.json        demo-mode sessions (synthetic, documentation IPs only), labelled "Demo data"
```

- Terraform reads `regions.yaml`, `budget.yaml`, `retention.yaml` with `yamldecode(file(...))`. AWS provider 6.x supports a per-resource `region` argument, so one provider block can `for_each` over regions (verify in Phase 0; fall back to provider aliases generated per region if needed).
- Lambdas read config from a versioned `config/` copy uploaded to S3 at deploy and cached per container. A config change is a deploy, not a code change.
- The web app fetches `config/public/*.json` (copy, theme, classes) built from YAML at build time and served from the public bucket.
- JSON Schemas in `config/schema/` validate every config file in CI.

## 12. Local development

```bash
make lab-up          # docker compose -f lab/compose.yml up -d
```

| Service | Image | Notes |
|---|---|---|
| `cowrie` | `cowrie/cowrie` pinned digest + our config | network `honeynet` (`internal: true`), port 2222 mapped to localhost only |
| `opencanary` | built from `sensor/opencanary/Dockerfile` | `honeynet` |
| `vector` | `timberio/vector` pinned | ships to moto S3 |
| `moto` | `motoserver/moto` | S3, SQS, DynamoDB, SSM stand-ins |
| `pipeline` | built | runs the Lambda handlers in a loop against moto |
| `replayer` | built | replays sanitised recorded sessions (`lab/replays/*.yaml`) into the sensors with original timing (asyncssh) |
| `outside` | `busybox` | on a separate network; the egress check proves sensors cannot reach it |
| `web` | Vite dev server | `VITE_DATA_MODE=lab`, reads the moto public bucket |

The UI also runs alone with `VITE_DATA_MODE=demo` on `config/seed/demo/` (Phases 2–3).

## 13. Testing strategy

| Level | Tool | What |
|---|---|---|
| Unit (Python) | pytest, hypothesis | parsers on recorded logs, redaction (property tests: no IP pattern survives), pseudonymiser, features, labelling functions, codename mapping |
| Integration (Python) | pytest + moto | each Lambda handler end to end on moto S3/SQS/DynamoDB |
| ML | pytest + eval script | features deterministic; model loads in ONNX and matches sklearn/LightGBM output within tolerance; eval report regenerates; no leakage across the temporal split |
| Infra unit | `terraform test` with `mock_provider "aws"` | egress rules, IAM, tags, buckets private, lifecycle, budget exists |
| Infra static | tflint, Trivy config scan, Checkov | misconfigurations |
| Infra cost | Infracost | cost diff posted in PR (as a CI artifact; no paid API) |
| Sensor | pytest in privileged container | nftables behaviour, Cowrie config, file-delete unit |
| Lab end to end | `make lab-up lab-attack` + pytest | replayed attack appears in the public feed, redacted, classified |
| Web unit | Vitest + Testing Library | state, scheduling of arcs, replay timing, redaction rendering |
| Web e2e | Playwright + `@axe-core/playwright` | every screen in demo mode; keyboard paths; reduced motion; zero serious/critical axe issues |
| Visual | Playwright screenshots (`toHaveScreenshot`) | globe and replay, with WebGL in a fixed seed |
| Real cloud | manual scripts, Phases 5–6 only, after Nour's "yes" | egress probe, first-attack check, cost check |

CI never touches real AWS or the internet beyond package registries.
