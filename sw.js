// Offline support for the Moon phases simulator.
// The page itself is fetched fresh whenever you're online (so updates show up straight
// away) and comes from the cache when you're not. Everything else (three.js, images,
// icons) never changes within a build, so it is served from the cache.
// build.py fills in CACHE (changes with every build) and FILES.
const CACHE = "moon-phases-v8";
const FILES = [
  "./assets/earth.webp",
  "./assets/moon.webp",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./",
  "./manifest.webmanifest",
  "./vendor/three/build/three.module.min.js",
  "./vendor/three/examples/jsm/controls/OrbitControls.js",
  "./vendor/three/examples/jsm/lines/Line2.js",
  "./vendor/three/examples/jsm/lines/LineGeometry.js",
  "./vendor/three/examples/jsm/lines/LineMaterial.js",
  "./vendor/three/examples/jsm/lines/LineSegments2.js",
  "./vendor/three/examples/jsm/lines/LineSegmentsGeometry.js"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(f => new Request(f, { cache: "reload" })))));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key !== CACHE) await caches.delete(key);
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  if (req.mode === "navigate") {
    // network first, so a new build is picked up as soon as it is published
    event.respondWith((async () => {
      try {
        const fresh = await fetch(req, { cache: "no-cache" });
        const path = new URL(req.url).pathname, home = new URL(self.registration.scope).pathname;
        if (fresh.ok && (path === home || path === home + "index.html")) (await caches.open(CACHE)).put("./", fresh.clone());
        return fresh;
      } catch (e) {
        const path = new URL(req.url).pathname, home = new URL(self.registration.scope).pathname;
        if (path !== home && path !== home + "index.html") return Response.redirect(self.registration.scope, 302);
        return (await caches.match("./", { cacheName: CACHE })) || Response.error();
      }
    })());
    return;
  }
  event.respondWith(caches.match(req, { cacheName: CACHE, ignoreSearch: true }).then(hit => hit || fetch(req)));
});
