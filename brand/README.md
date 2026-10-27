# Darb Ki brand

Ki is a Darb product. It wears Darb's colours (night, forest, gold, ivory) and has its own mark: **your gold beacon on the night globe, with hostile threads arriving from every side of the world.** In the show, a fighter feels a hostile ki (気) from across the planet before ever seeing it. Ki feels every attack land on your sensors. The thread colours are the attacker classes the app sorts: ember for crypto-miners, bone for bots, teal for humans typing by hand.

The hero image says "honeypot" in one picture: a honeycomb whose centre cell glows like an easy meal, with hostile threads curling in and ending inside it, caught and recorded.

Chosen by Nour from four meaning-led directions (A "The Watchtower" for the icon, B "The Lure" for the hero; C "Eyes Closed" and D "気, Struck" are kept in `concepts/`).

## See it

```sh
cd brand && npm install
node scripts/serve.mjs          # http://127.0.0.1:4180/ : brand sheet with every asset
```

## Rebuild every asset

```sh
npm run build                   # renders the two masters in Blender Cycles, then cuts everything
RENDER=0 npm run build          # reuses masters/ (no Blender needed) and rebuilds the flat assets
BLENDER=/path/to/blender npm run build   # when blender is not on PATH
```

Nothing is drawn by hand and nothing is hardcoded in the build:

| File | Holds |
|---|---|
| `src/tokens.json` | colours and roles (including the three attacker classes), type, the globe (beacon, thread origins, lift, graticule, camera), render samples, icon sizes, copy |
| `src/globe.mjs` | the globe, great-circle threads and projection for the flat SVG marks, from the same `tokens.globe` numbers the render uses |
| `src/render.py` | Blender scene: the watchtower globe (`tile`) and the honeycomb lure (`hero`) |
| `scripts/build.mjs` | renders the masters, cuts every icon, writes the SVG marks, wordmarks, social cards, manifest and CSS tokens |
| `masters/` | the two Blender renders, committed so the flat assets rebuild without Blender |
| `concepts/` | the four directions and `blender/ki.py`, the script that rendered them |

## What's in `exports/`

| Path | Use |
|---|---|
| `icons/icon-192.png`, `icon-512.png` | PWA icons, purpose `any` (squircle cut) |
| `icons/icon-maskable-192.png`, `-512.png` | PWA maskable (globe inside the 80% safe zone) |
| `icons/apple-touch-icon.png` | iOS home screen, 180 px, opaque |
| `icons/icon-desktop-1024.png` | Desktop: macOS grid, 824 px body with system shadow |
| `icons/favicon.ico`, `favicon.svg`, `favicon-16/32/48.png` | Browser tab: no graticule, three heavy threads and a big beacon, so it reads at 16 px |
| `icons/badge-96.png` | Notification badge and Android monochrome icon |
| `svg/mark-on-night.svg` | The flat mark on its night tile, threads in class colours |
| `svg/mark-gold.svg`, `mark-ivory.svg`, `mark-ink.svg` | The globe alone, for any background |
| `svg/wordmark-on-dark.svg`, `-on-light.svg` | Lockup: mark, Darb, Ki, 気 (text outlined, no font needed) |
| `social/og-image.png`, `social/hero.png` | 1200 x 630 sharing card and 2400 x 1260 README hero |
| `manifest.webmanifest`, `head.html`, `tokens.css` | Drop-in PWA manifest, `<head>` tags and CSS tokens |

## Rules

- Ember, bone and teal always mean miners, bots and humans. Never use them as decoration, and never show colour as the only signal (the app labels every class).
- Threads always end on your beacon: attacks come to you, never from you. The sensors cannot open outbound connections, and the brand never suggests they do.
- No stock "cyber attack map" look: no neon grids, skulls, hooded figures or matrix rain.
- Darb's doorway outline belongs to Darb itself; Ki never uses it.
- Every visual is original and made in code. No official Dragon Ball art, logos, characters or audio.
- Fonts: Zen Antique (display), Geist (interface) and Yuji Boku (気 only), all under the SIL Open Font License (`fonts/`).
