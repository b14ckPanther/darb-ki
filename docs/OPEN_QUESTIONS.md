# Open questions (only Nour can decide)

The agent asks these in Phase 1, **one at a time**, open-ended first, in this order. Record each answer here (move it to "Answered" with the date) and in `DECISIONS.md`.

## Open-ended (ask first)

1. When you open Darb Ki in the morning, what do you want to see or feel in the first five seconds? What would make you open it every day?
2. Who is the main audience for the public site: recruiters, security engineers at companies like Check Point and Wiz, or other developers? What should they think after 10 seconds?
3. Which of the three art directions in `UI_DESIGN.md` §4 (Night Cartography, Instrument Panel, Weather System) feels right, or what would you change? Any references you love (not security "attack maps")?
4. What should the replay feel like: a cinematic re-enactment, or a precise forensic record? Where on that line?
5. In Darb Budokai, how should the Watchtower matter to the game, given we should reward keeping the watch, not the number of attacks?

## Scope and safety

6. Have you read the legal and ethics note (`VISION.md` §6) and the egress rules (`ARCHITECTURE.md` §4)? Anything you want stricter?
7. Do you want the extra classes `scanner` and `unknown` alongside bots, crypto-miners and humans?
8. Showing the attacker's network owner (ASN org, e.g. a hosting company) publicly: yes or no?
9. Showing commonly tried usernames and passwords publicly (only those on a public default-credentials list): yes or no?
10. Should the public site be fully public, or unlisted until launch? Should Watchtower Status (sensor health, cost) ever be online, or stay local only?
11. Contributing anonymised data to community feeds (for example AbuseIPDB reports): default is **no**. Do you want it later?
12. If a session shows an attack on an identifiable third party, how do you want to handle disclosure (private note only, or report to the victim or CERT-IL)?

## Cloud and cost

13. Which AWS account will this run in? Is it new (free-plan credits) or existing? Is IAM Identity Center (SSO) set up?
14. Budget alarm amount: $40/month proposed. Different?
15. Regions: `us-east-1`, `eu-central-1`, `ap-southeast-1` proposed, pipeline in `eu-central-1`. Add `il-central-1` (Tel Aviv) as a local-interest sensor? Start with one region only?
16. On-demand (~$38/month for 3 regions) or spot (~$23, occasional gaps)?
17. Raw data retention: 30 days proposed. Shorter?
18. How long should it run: a fixed period (for example 3 months for the dataset and write-up) or indefinitely?
19. Domain: a subdomain of `zangeel.dev` (for example `watchtower.zangeel.dev`)? Where is `zangeel.dev` DNS hosted?

## Stack and repo

20. Repo name `darb-ki`, private while building, MIT licence: OK?
21. Web stack: keep React + Three.js (proposed), or use this project to also show another frontend stack?
22. GeoIP source: DB-IP Lite (no account, CC BY attribution) or MaxMind GeoLite2 (free account and key)?
23. Gold set for evaluation: how many sessions are you willing to hand-label (300 proposed, about 1–2 hours with the keyboard labelling screen)?
24. Sound: optional procedural tones per class, off by default. Want it at all?

## Answered

| # | Date | Answer | ADR |
|---|---|---|---|
| | | | |
