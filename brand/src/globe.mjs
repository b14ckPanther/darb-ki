// The Darb Ki globe as geometry, shared by the flat SVG marks; src/render.py builds the 3D globe from the
// same tokens.globe numbers (beacon, thread origins, lift), so the flat mark and the render agree.
// Units: globe radius = tokens.globe.radius, z up, the camera looks along +y from tokens.globe.camera.

const rad = (d) => (d * Math.PI) / 180
const norm = (v) => { const l = Math.hypot(...v); return v.map((x) => x / l) }
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

/** A point on the sphere at latitude/longitude (degrees). Longitude 0 faces the camera. */
export function sph(lat, lon, r) {
  return [r * Math.cos(rad(lat)) * Math.sin(rad(lon)), -r * Math.cos(rad(lat)) * Math.cos(rad(lon)), r * Math.sin(rad(lat))]
}

/** A great-circle arc from a to b, lifted off the surface in the middle like a thrown thread. */
export function arc(a, b, r, lift, n = 48) {
  const A = norm(a), B = norm(b)
  const omega = Math.acos(Math.min(1, Math.max(-1, dot(A, B))))
  return Array.from({ length: n + 1 }, (_, i) => {
    const t = i / n
    const s = Math.sin(omega) || 1
    const k1 = Math.sin((1 - t) * omega) / s, k2 = Math.sin(t * omega) / s
    const p = norm([A[0] * k1 + B[0] * k2, A[1] * k1 + B[1] * k2, A[2] * k1 + B[2] * k2])
    const h = r * (1 + lift * Math.sin(Math.PI * t))
    return p.map((x) => x * h)
  })
}

/** Orthographic view from the camera direction: [x, y, depth]; depth > 0 faces the viewer. */
export function viewer(G) {
  const d = norm(G.camera.map((c, i) => c - G.target[i]))
  const right = [1, 0, 0]
  const up = norm([0, 0, 1].map((z, i) => z - dot([0, 0, 1], d) * d[i]))
  return (p) => [dot(p, right), dot(p, up), dot(p, d)]
}

/** The scene's parts in globe space. */
export function globeParts(G) {
  const beacon = sph(...G.beacon, G.radius)
  const threads = G.threads.map(([la, lo, kind], i) => {
    const from = sph(la, lo, G.radius)
    return { kind, from, pts: arc(from, beacon, G.radius, G.lift + G.liftStep * (i % 3)) }
  })
  const lat = [], lon = []
  for (let a = -90 + G.graticule; a < 90; a += G.graticule) lat.push(Array.from({ length: 121 }, (_, i) => sph(a, -180 + 3 * i, G.radius)))
  for (let b = 0; b < 180; b += G.graticule) lon.push(Array.from({ length: 121 }, (_, i) => sph(-90 + 1.5 * i, b, G.radius)), Array.from({ length: 121 }, (_, i) => sph(-90 + 1.5 * i, b + 180, G.radius)))
  return { beacon, threads, graticule: [...lat, ...lon] }
}
