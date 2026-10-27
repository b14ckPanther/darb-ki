# Vision

## 1. Intent

Show, in public and with real data, that Nour can run cloud infrastructure safely under real attack, build a data pipeline on it, train a model that means something, and present it as a piece of visual work people want to look at.

The honeypots are fake servers that look like easy targets. Real attackers find them within minutes. The project records what they try, sorts them into kinds (bots, crypto-miners, humans typing by hand), and draws it as a living globe. Click an arc and you watch the attacker's session replay keystroke by keystroke, with anything identifying or dangerous removed.

## 2. Goals

1. **A globe people stop scrolling for.** Attacks arc in live from around the world onto Nour's sensors. Quality bar: "jaw-dropping", never a dashboard template.
2. **Session replay.** Click an arc, replay exactly what was typed, at real speed, with the model's verdict and the reasons behind it.
3. **Real, reproducible infrastructure.** Everything in Terraform: multi-region sensors, the pipeline, the public site, a budget alarm. One command brings it up, one command tears it down.
4. **Provable isolation.** Layered egress controls, automated tests that prove them, and a tripwire that stops a sensor if anything ever leaves it.
5. **An honest ML model.** Session classifier with a published model card: data, labelling method, precision/recall per class, confusion matrix, known failure modes. Unsupervised clustering to find attacker "families".
6. **Privacy by design.** No attacker IP in any public view. Raw data retained briefly and privately.
7. **Daily use for Nour.** A morning glance at the Watchtower: what came in overnight, anything unusual (a human), and the cost so far this month.

## 3. Non-goals

- Not a high-interaction honeypot. No real shells, no real OS for attackers.
- Not a malware lab. No sample collection, detonation, sandboxing or sharing.
- Not threat intelligence for sale or a public IP blocklist (contributing to AbuseIPDB is an open question, default off).
- Not an IDS/SIEM for protecting real systems.
- No hack-back, attribution of individuals, or contact with attackers.
- Not a general AWS showcase: only the services the design needs.

## 4. Anti-goals (failure even if it works)

- Any sensor is ever able to send traffic to a third party. Even once. This ends the project.
- A malware sample or a working payload URL is published or committed.
- A real attacker IP, or a credential that could belong to a real third party, shows up on the public site, a screenshot or the demo GIF.
- A surprise AWS bill. Anything above the budget alarm without Nour knowing.
- The globe looks like a stock "cyber attack map" (neon on black, laser beams, matrix rain, glowing skull).
- The classifier's accuracy is claimed without a held-out evaluation, or the demo shows only cherry-picked sessions.
- Fake "live" data in a mode not labelled as demo.

## 5. Why this stack for the Israeli junior market

From 431 Israeli listings: Cloud 256, AWS 191, AI 287, Python 178, Kubernetes 146. Nour's GitHub today is ~90% Next.js/Supabase/TypeScript, with no cloud infrastructure or ML.

- **AWS + Terraform** prove infrastructure as code across regions, IAM least privilege, VPC design, and cost control: the most requested cloud skills.
- **Security** fits Israel's security employers (Check Point, CyberArk, Wiz, Palo Alto's local teams). A honeypot with provable isolation and a written ethics note is a concrete talking point in a security interview.
- **Python ML** on a real, messy, self-collected dataset (feature engineering, weak labelling, clustering, evaluation, ONNX export) is stronger than any tutorial dataset.
- **The globe** keeps Nour's frontend strength visible and gives recruiters a 10-second reason to click.

## 6. Legal and ethics note

Written by the planning step, not a lawyer. **Not legal advice.** Nour should read it before Phase 6 and decide the open questions in `OPEN_QUESTIONS.md`.

**What the project does.** It runs passive decoys. Nobody is invited or tricked into connecting. Attackers connect on their own to an address that was never advertised. The sensors only answer. They never reach out, scan, or retaliate.

**AWS.** Running honeypots on EC2 is allowed under the AWS Acceptable Use Policy as long as the instances are not used to attack, relay, or host abusive content. The egress design (ARCHITECTURE §4) is what keeps us inside that policy. If AWS sends an abuse report, stop the affected sensor first, investigate second.

**Personal data.** IP addresses can be personal data under the GDPR and Israel's Protection of Privacy Law (as amended, including Amendment 13 in force since August 2025). The project's lawful basis is legitimate interest in security research. It follows these principles:
- **Minimisation:** collect only connection metadata, credentials tried, and commands typed. No file content.
- **Pseudonymisation:** public views show a keyed pseudonym, never the IP (ARCHITECTURE §7).
- **Coarse location:** public coordinates are snapped to a city or country centroid, never the raw GeoIP point.
- **Retention:** raw data with IPs is deleted after the retention period in config (30 days proposed) by an S3 lifecycle rule. Public data is aggregated or pseudonymised.
- **Security:** raw buckets are private, encrypted (SSE-S3), with no public access, versioning off for raw logs, and access only through Nour's SSO role.
- **Transparency:** a public "Method and ethics" page explains all of this.

**Third-party data inside attacker input.** Attackers type passwords, IPs and URLs that can belong to other victims. Public transcripts redact IPs, domains, URLs, emails and any password not on a public default-password list in config.

**Malware.** Never collect, store, share or upload samples. Hash and delete on the sensor. Publishing hashes is fine; publishing samples or live download URLs is not.

**Entrapment and "hacking back."** Not applicable: the decoys are passive, and the project never touches attacker systems.

**Responsible disclosure.** If a session shows an attack on a specific identifiable third party (for example credentials of a real company), do not publish it. Note it privately and ask Nour whether to report it to that party or to CERT-IL (gov.il National Cyber Directorate).

## 7. Success measures (proposed, confirm with Nour in Phase 1)

- Sensors up in 3 regions for 30 days with zero outbound connections in VPC flow logs.
- First real attack recorded within 1 hour of first deploy.
- Classifier macro-F1 reported on a held-out, hand-labelled set (target set with Nour in Phase 7, not invented here).
- Globe at 60 fps on a 2020-era laptop, Lighthouse performance ≥ 85 on mobile.
- Monthly cost within the budget alarm for every month it runs.
