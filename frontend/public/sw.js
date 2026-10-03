const CACHE_NAME = 'docta-v2';
const ASSETS_TO_CACHE = [
  '/favicon.svg',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Pass API requests directly to network
  if (event.request.url.includes('/api/')) {
    return;
  }

  // Always fetch the app shell from the current deployment first. Caching
  // index.html indefinitely can leave it pointing at deleted hashed assets.
  if (event.request.method === 'GET' && event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(event.request);
        if (response.ok) {
          const cache = await caches.open(CACHE_NAME);
          await cache.put('/index.html', response.clone());
        }
        return response;
      } catch {
        const cachedShell = await caches.match('/index.html');
        return cachedShell || Response.error();
      }
    })());
    return;
  }

  // Let the browser fetch scripts, styles, images, and fonts directly. These
  // files are content-hashed by Vite and should come from the same deployment
  // as the HTML; a service-worker cache can otherwise mix deployment versions.
});
