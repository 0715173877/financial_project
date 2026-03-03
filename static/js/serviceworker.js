// Static cache name
const staticCacheName = 'django-pwa-v1';

// Assets to cache
const assets = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/images/icon-192x192.png',
    '/static/images/icon-512x512.png',
    // Add other static assets you want to cache
];

// Install event
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installed');
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                console.log('Caching shell assets');
                return cache.addAll(assets);
            })
            .catch(err => {
                console.log('Error caching assets:', err);
            })
    );
});

// Activate event
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activated');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== staticCacheName) {
                        console.log('Service Worker: Clearing Old Cache');
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Fetch event
self.addEventListener('fetch', (event) => {
    console.log('Service Worker: Fetching');
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
            .catch(() => {
                // If both fail, show offline page
                return caches.match('/offline/');
            })
    );
});


// ... previous code ...

// Fetch event with offline page
self.addEventListener('fetch', (event) => {
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return caches.match('/offline/');
                })
        );
    } else {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    return response || fetch(event.request);
                })
        );
    }
});