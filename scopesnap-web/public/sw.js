/**
 * SnapAI Service Worker
 * Provides offline shell caching for the PWA.
 * Caches the app shell (HTML, CSS, JS) for offline access.
 * API calls are always network-first (no offline data caching).
 */

const CACHE_NAME = "scopesnap-shell-v1";

// App shell files to cache on install
const SHELL_FILES = [
  "/dashboard",
  "/assess",
  "/offline",
];

// Install: cache the app shell
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Best-effort cache — don't fail install if some pages aren't available
      return Promise.allSettled(
        SHELL_FILES.map((url) => cache.add(url).catch(() => null))
      );
    })
  );
  self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// Fetch: network-first for API, cache-first for shell
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // API calls: always network-first
  if (url.pathname.startsWith("/api/") || url.hostname === "localhost" && url.port === "8001") {
    event.respondWith(fetch(event.request));
    return;
  }

  // Static assets (JS, CSS, images): cache-first
  if (
    url.pathname.startsWith("/_next/static/") ||
    url.pathname.match(/\.(png|jpg|svg|ico|woff2?)$/)
  ) {
    event.respondWith(
      caches.match(event.request).then(
        (cached) => cached || fetch(event.request).then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
      )
    );
    return;
  }

  // Navigation: network-first, fallback to cached shell
  event.respondWith(
    fetch(event.request).catch(() =>
      caches.match(event.request).then(
        (cached) => cached || caches.match("/dashboard")
      )
    )
  );
});
