# Integration with the universe

Darb Ki works fully on its own. Sending events to Darb Budokai is a **later, optional phase** (Phase 9 in `PLAN.md`) and must never block or slow the core.

Darb Budokai's contracts (`/Users/zangeel/Documents/GitHub/darb-budokai/docs/EVENT_CONTRACTS.md`): every event is a **CloudEvents 1.0** envelope in structured JSON mode with Darb Budokai extensions, the payload is validated by a **JSON Schema 2020-12** file per type and major version, and producers post to Darb Budokai's `POST /ingest/v1/events` with HMAC headers. Darb Budokai's contracts do not yet list Darb Ki events, so the types below are **proposed, confirm with Nour in Phase 1**, and must be added to Darb Budokai's `EVENT_CONTRACTS.md` (and its `config/rulebook/v1/`) in Darb Budokai's repo when integration happens.

## 1. What Darb Budokai does with them (game meaning, proposed)

Attackers are **invaders at the borders**. Each night, the Watchtower reports the siege: how many came, of what kind. A human attacker is a rare "scout" who gets a named entry in the battle log. Possible effects (Darb Budokai's rulebook decides, not this project): a border-region fog/light change, a "Watchtower held" daily quest when sensors stayed healthy and isolated all day, a small Vigilance stat for keeping the watch.

The game must not reward more attacks (Nour cannot cause them, and it would be the wrong incentive). It rewards **keeping the watch**: uptime, zero egress incidents, labelled sessions, model improvements.

## 2. Events emitted

Source: `urn:budokai:producer:darb-ki`. Producer scope: `watchtower.*`. All events carry `budokaiuserid` (Nour's Darb Budokai user id, from env), `budokaievidence.tier = "verified"` with `ref` pointing to the daily stats object, and `budokaimode = "live"` (or `"demo"` from the seed mode). IDs are UUIDv5 over a natural key so re-sending is idempotent.

**Privacy:** no event contains an IP, a raw location, a credential, or a command. Only counts, classes, codenames and coarse regions.

### `watchtower.siege.summarized` v1

Once per day, after the nightly aggregate.

```json
{
  "date": "2026-11-03",
  "timezone": "Asia/Jerusalem",
  "sessions": 4812,
  "byClass": { "bot": 4390, "miner": 211, "human": 3, "scanner": 180, "unknown": 28 },
  "sensorsUp": 3,
  "sensorsConfigured": 3,
  "uptimeRatio": 0.998,
  "egressIncidents": 0,
  "topOriginCountries": ["CN", "US", "NL"],
  "modelVersion": "v3",
  "summaryUrl": "https://<public-site>/today?date=2026-11-03"
}
```
Required: `date`, `timezone`, `sessions`, `byClass`, `sensorsUp`, `sensorsConfigured`, `egressIncidents`, `modelVersion`. Natural key: `date`.

### `watchtower.human.sighted` v1

When a session is classified `human` with confidence above the threshold in config. At most the daily cap in config (to keep it rare and meaningful).

```json
{
  "sessionPseudoId": "s_7Q2M9K",
  "codename": "Slate Heron",
  "region": "eu-central-1",
  "originCountry": "BR",
  "startedAt": "2026-11-03T02:14:09Z",
  "durationSeconds": 412,
  "commandCount": 37,
  "confidence": 0.91,
  "replayUrl": "https://<public-site>/s/s_7Q2M9K"
}
```
Required: `sessionPseudoId`, `codename`, `region`, `startedAt`, `durationSeconds`, `confidence`. Natural key: `sessionPseudoId`.

### `watchtower.breach.contained` v1

Emitted if the tripwire ever fires and quarantines a sensor. Expected never. It exists so an incident is visible in Darb Budokai too, as a defeat, not a reward.

```json
{ "sensorRegion": "us-east-1", "detectedAt": "2026-11-03T02:14:09Z", "action": "quarantined_and_stopped", "incidentId": "inc_20261103_01" }
```
Natural key: `incidentId`.

### `watchtower.model.promoted` v1

When Nour promotes a new model version (manual step in Phase 7).

```json
{ "modelVersion": "v3", "previousVersion": "v2", "macroF1": 0.0, "evaluatedOn": 312, "promotedAt": "2026-11-03T10:00:00Z" }
```
The number is filled from the real eval report; never invented. Natural key: `modelVersion`.

## 3. Files in this repo

```
contracts/events/
├── watchtower.siege.summarized/v1.schema.json   + examples/valid-*.json, invalid-*.json
├── watchtower.human.sighted/v1.schema.json
├── watchtower.breach.contained/v1.schema.json
└── watchtower.model.promoted/v1.schema.json
```

- Written in Phase 8 (aggregate) with tests: every example validates (or fails) as labelled, using `jsonschema` (Draft 2020-12).
- Versioning follows Darb Budokai's rules: additive optional fields stay in `v1`; anything else is `v2` alongside `v1`, plus an ADR.

## 4. Outbound adapter

- The nightly aggregate Lambda writes events into `s3://ki-raw-central/outbox/<date>/<eventId>.json`. This is the outbox: always written, whether Darb Budokai exists or not.
- `adapters/budokai/` (Python) reads unsent outbox objects, wraps them in the CloudEvents envelope, signs with `X-Budokai-Producer` and `X-Budokai-Signature: t=<unix>,v1=<hex HMAC-SHA256(secret, t + "." + body)>` (Darb Budokai ARCHITECTURE §8), posts in batches to `POST /ingest/v1/events:batch`, and marks objects sent (S3 object tag). 202 duplicates are success.
- Disabled unless `REALM_INGEST_URL`, `REALM_PRODUCER_KEY_ID` and `REALM_PRODUCER_SECRET` are set. Runs as a scheduled Lambda in the cloud, or `make budokai-sync` locally.
- Tests: WireMock-style fake ingest server (pytest + `pytest-httpserver`) verifies signature format, batching, retry with backoff, idempotency. Never calls a real Darb Budokai in CI.

## 5. Consumed

Nothing. Darb Ki does not read from Darb Budokai or any sibling.

## 6. Other siblings

- **Darb Enmacho** may subscribe to the same outbox (or Darb Budokai's topics) to archive `watchtower.*` events into BigQuery. No change needed here beyond keeping schemas stable.
- **Darb Kaioken** publishes the write-up with honest numbers taken from the public stats files and the model card.
- **Darb Genki** is unrelated at runtime (it observes Darb Budokai's services, not this AWS stack).

## 7. Integration phase checklist (Phase 9)

1. Ask Nour whether Darb Budokai's ingest is running and whether to integrate now.
2. Open a PR in Darb Budokai's repo adding the four event types to `EVENT_CONTRACTS.md`, the schemas, the producer key scope `watchtower.*`, and rulebook entries (Nour decides the game effects).
3. Run the adapter against Darb Budokai locally (Darb Budokai's compose stack), check the battle log shows the siege.
4. Only then enable the scheduled adapter in the cloud (after Nour's "yes").
