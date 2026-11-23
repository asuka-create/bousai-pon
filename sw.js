'use strict';
// まもってポン！ Service Worker
// 中身を変えたら VERSION を上げる（古いキャッシュが消えて新しいファイルに入れかわる）
const VERSION = 'v1.4.0';
const CACHE = 'bousaipon-' + VERSION;
const FILES = ['./', './index.html', './manifest.webmanifest', './icon.svg', './icon-192.png', './icon-512.png', './icon-180.png', './shelters-sagamihara.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('bousaipon-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;

  // ページ本体：ネットがつながれば最新、つながらなければ保存したもの
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)); return res; })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  // 画像など：保存したものを先に使う
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
