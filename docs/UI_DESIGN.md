# UI design

Fixed by Nour's roadmap: a live 3D globe with attacks arcing in from around the world; click one to replay exactly what the attacker typed; in Darb Budokai, attackers are invaders at the borders. Quality bar: "jaw-dropping", never a stock "cyber attack map".

Everything else here (art directions, layouts, names, motion values) is **proposed, confirm with Nour in Phase 1**. Phase 2 turns the chosen direction into a design system. Phase 3 builds every screen on demo data, approved one screen at a time.

## 1. The signature moment

**"The Watchtower at night."** The page opens on a dark, slowly turning globe. Nour's sensors sit on it as small, steady beacons (one per region). Every few seconds an attack arrives: a thin arc lifts off from a city on the other side of the world, climbs, and lands on a beacon, which answers with a brief ring of light. The arc's colour and rhythm tell you what it is before you read anything:

- **Bots:** short, fast, identical arcs in tight bursts, like rain. Most of the traffic.
- **Crypto-miners:** heavier arcs that leave a slow-fading trail and a faint ember where they land.
- **Humans typing by hand:** rare. The arc draws slowly, almost hesitant, and the beacon it lands on holds a soft pulse for as long as the session lasted. A small, quiet notice appears: "A human is at the gate."
- **Scanners:** barely visible flickers at the beacon, no arc (just knocking).

**The replay.** Click (or press Enter on) any arc. The globe eases its camera toward the attacker's region and dims. A panel slides in and the session replays at real speed: the login attempts first (password tries tick by), then the shell. Each keystroke appears with its real timing, including typos and backspaces, so a human feels human and a bot feels like a machine gun. Redactions appear as clean inline tokens (`[ip]`, `[url]`) rather than black bars. On the side: the codename ("Slate Heron"), coarse origin, the model's verdict with its confidence and the evidence chips that led to it ("keystroke gaps vary like a person's", "checked CPU count before downloading"). A scrubber lets you jump, speed up (1x, 4x, 16x) or skip idle time.

**Why it lands:** the globe is beautiful at a glance and honest up close. The replay turns an abstract arc into a person or a machine you can watch think.

## 2. Screens and surfaces

| # | Screen | Purpose | Key content |
|---|---|---|---|
| 2.1 | **Globe (home)** | The signature view | Globe, live counter strip (sessions in the last hour, by class), "live, about 2 minutes behind" indicator, class legend that doubles as a filter, a ticker of the latest few sessions as a list (accessible equivalent of the arcs) |
| 2.2 | **Session replay** | Watch one attack | Transcript replay, scrubber, speed, verdict + confidence + evidence chips, credentials tried (redacted per policy), file hashes (no links), codename, coarse origin, sensor region, duration. Side panel on desktop, sheet with detents on mobile. Shareable URL `/s/<sessionPseudoId>` |
| 2.3 | **Today and history** | The daily-use view for Nour | Small multiples: sessions per hour by class, top tried usernames and passwords (public list only), top command families, regions most hit; date picker for past days. Built with the `dataviz` skill. |
| 2.4 | **Clans** | The clustering result | Attacker families found by HDBSCAN: a constellation layout where each clan is a cluster of points; click a clan for its typical command sequence, size, first/last seen, and two example replays |
| 2.5 | **Model** | Honest ML | Model card rendered from `ml/model_card.md` data: dataset size, labelling method, per-class precision/recall, confusion matrix, known failure modes, version and date |
| 2.6 | **Method and ethics** | Trust | How the sensors are isolated (a simple diagram of the seven layers), what is collected, what is hidden, retention, malware policy, DB-IP and Natural Earth attribution |
| 2.7 | **Watchtower status (private, local only)** | Nour's ops view, not deployed publicly | Sensor heartbeat per region, egress tripwire status (should always read "no outbound connections"), month-to-date cost vs budget, last pipeline error. Runs only with `VITE_DATA_MODE=lab` or against a private endpoint decided in Phase 8 |
| 2.8 | **Labelling (private, local only)** | Build the gold set for Phase 7 | One session at a time, keyboard-first: `b` bot, `m` miner, `h` human, `s` scanner, `u` unsure, `n` next. Writes to `data/private/labels.jsonl` |
| 2.9 | **Empty, loading, error, offline, demo** | States | Globe idle state ("quiet night" with only beacons), loading skeleton for replay, feed error with retry, WebGL unavailable fallback (2D equirectangular map with the same data), persistent "Demo data" banner in demo mode |

Navigation: desktop uses a slim top bar (Globe, Today, Clans, Model, Method). Mobile uses a bottom tab bar (Globe, Today, Clans, More) with large collapsing titles on the non-globe screens.

## 3. Interaction and motion rules

- **One focal motion at a time.** While a replay plays, the globe slows and dims. Never two competing animations.
- **Motion carries meaning.** Arc speed, height and trail length encode class (values in `config/theme/*.yaml`). No decorative motion that does not encode something.
- **Springs, not linear.** UI panels and sheets use spring physics (stiffness/damping from theme config). Arcs use eased curves along a great-circle path; altitude scales with distance.
- **Pressed-state feedback:** interactive elements scale to about 0.97 on press with a spring return.
- **Camera:** gentle auto-rotate (pauses on any interaction and for 10 s after), drag to orbit with damping, scroll/pinch to zoom within limits, double-click to recentre. Keyboard: arrow keys orbit, `+`/`-` zoom, `Tab` cycles through the latest sessions list, `Enter` opens replay, `Esc` closes, `Space` play/pause replay, `[`/`]` change speed.
- **Bursts are throttled.** A bot storm of hundreds of sessions renders as batched arcs (instanced) with a cap from config, plus an honest counter ("+214 more"), never dropped silently.
- **Sound:** off by default. Optional soft tones per class made with `procedural-sfx`, toggle in settings, never autoplay.
- **Performance budget:** 60 fps on a 2020-era laptop, 30 fps floor on a mid-range phone; instanced arcs; device-pixel-ratio capped at 2; pause rendering when the tab is hidden.

### Reduced motion (`prefers-reduced-motion: reduce`)

- No auto-rotate. Arcs appear as static lines that fade in and out over 300 ms, no travel. Beacon pulses become a static highlight.
- Replay shows the transcript line by line (one line per step) instead of per keystroke, with timing shown as text ("typed over 4.2 s").
- Camera moves become instant cuts.

## 4. Art direction: three candidates (Nour picks one in Phase 1)

All three avoid: neon green on black, laser beams, matrix rain, skulls, hooded figures, padlock icons, red "DANGER" styling, gradient blobs, stock "cyber" imagery.

### A. "Night Cartography" (proposed default)

The globe as an engraved, matte night-time relief: ocean near-black ink, land in fine contour hatching (custom shader), no textures of the photo Earth kind. Beacons are warm brass points. Arcs are thin luminous threads in a restrained palette: bots a cool bone-white, miners ember orange, humans a verdigris teal, scanners a faint grey. Typography: a high-contrast serif for headings (Fraunces or Cormorant, Google Fonts), a crisp grotesk for UI (Inter Tight), a monospace for transcripts (JetBrains Mono). Shares DNA with Darb Budokai's "Ember Atlas" direction, so the Watchtower feels like part of the same world.

### B. "Instrument Panel"

A precise scientific instrument: off-white paper globe with a hairline graticule, ink-blue arcs, small engineering labels with leader lines, like a survey chart under glass. A light theme with a dark mode. Typography: IBM Plex Sans + IBM Plex Mono. Calm, credible, very readable; strong for a security-company audience.

### C. "Weather System"

Attacks treated as weather. The globe is dark with a soft volumetric atmosphere rim. Bot storms render as fine particle rain bands sweeping across regions, miners as heat shimmer, humans as a single slow lightning-like thread. Typography: Space Grotesk + DM Mono. The most cinematic and the most expensive to build and keep at 60 fps.

Each candidate gets a still mock and a 10-second motion study in Phase 2 before Nour decides. Every asset is original or Google Fonts; record licences in `ASSETS.md`.

## 5. Native feel on mobile, icons, no emoji

Nour: "the apps must feel as native as a SWIFT UI when it comes to mobile apps... use only modern elements and icons and SVGs ... emojis and low quality icons are forbidden".

- **SwiftUI-like web on phones:** respect safe-area insets (`env(safe-area-inset-*)`), large collapsing titles on list screens, a bottom tab bar, sheets with detents (peek, half, full) and drag-to-dismiss for the replay and session detail, spring physics everywhere (no linear easing), pressed-state scale feedback, 44pt minimum touch targets, system-like translucent materials (`backdrop-filter` with a solid fallback), native-style lists with swipe actions (swipe a session in the latest list to "replay" or "copy link").
- **Icons:** one consistent modern SVG set, chosen in Phase 2: Solar via Iconify (skill `solar-duotone-bold`) or Lucide. Custom SVG glyphs for class marks (bot, miner, human, scanner) drawn in-repo in the same stroke style. Real company logos (AWS, Terraform in the README "built with" strip) only via Iconify Simple Icons (skill `company-logos`).
- **Emojis are forbidden** in UI, notifications, alerts, docs and commits. No raster clip-art, no mixed icon styles.

## 6. Accessibility requirements

- **Text alternative to the globe:** the latest sessions list is always present (visually and for screen readers) and carries the same information as the arcs. An `aria-live="polite"` region announces at most one summary per minute (rate from config), never every arc; humans arriving are announced individually.
- **Keyboard:** every control reachable and operable; visible focus ring (3:1 contrast against its background); logical tab order; replay fully controllable by keys (§3); skip link to the sessions list.
- **Colour:** class is never shown by colour alone. Arcs differ by colour, speed and dash pattern; the legend and chips use icon + text. WCAG AA contrast: 4.5:1 body text, 3:1 large text and UI components. Phase 2 adds an automated contrast test over all token pairs.
- **Reduced motion:** §3.
- **Responsive:** 360px and up. On small screens the globe takes the top half and the sessions list the rest; replay opens as a sheet.
- **Screen readers:** the replay transcript is a real text log (`role="log"`) with an option to read it all at once instead of streaming.
- **WebGL off or failing:** 2D map fallback with the same data and controls.
- **Axe:** zero serious or critical violations in Playwright on every screen in demo mode.

## 7. Frontend architecture (web/)

- Vite + React 19 + TypeScript strict. React Three Fiber scene for the globe; `three-globe` for geo helpers (great-circle arcs, polygons) where it fits, custom shaders for land, arcs and beacons. Final split decided in Phase 2 after running `threejs-choose-skills`.
- State: Zustand store fed by a `FeedSource` interface with three implementations: `DemoFeed` (seed JSON), `LabFeed` (moto bucket), `LiveFeed` (CloudFront). Selected by `VITE_DATA_MODE`.
- Scheduler: pure TypeScript module that maps event timestamps to render times (unit-tested without WebGL).
- Copy and theme loaded from `config/public/*.json`; no user-facing string literals in components (lint rule).
- Routing: React Router; `/`, `/s/:id`, `/today`, `/clans`, `/model`, `/method`.
- Styling: decided in Phase 2 (CSS Modules with design tokens as CSS variables proposed; Tailwind only if Nour prefers).
