// Service worker pour Robot Trading.
// Met en cache les fichiers statiques de l'app (structure, style, icônes)
// pour permettre l'installation sur l'écran d'accueil. Les données de
// signaux elles-mêmes (data/signals.json) ne sont JAMAIS mises en cache
// ici, pour que l'app affiche toujours les derniers signaux disponibles.

const CACHE_NAME = 'robot-trading-v1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Les signaux ne sont jamais mis en cache : toujours aller chercher
  // la version la plus fraîche sur le réseau.
  if (url.pathname.includes('/data/signals.json')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Pour le reste (structure de l'app), on sert depuis le cache d'abord,
  // avec le réseau comme solution de secours.
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
