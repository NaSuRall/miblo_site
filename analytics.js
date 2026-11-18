(() => {
  'use strict';
  const id = document.currentScript.dataset.measurementId;
  const banner = document.querySelector('[data-consent-banner]');
  const settings = document.querySelector('[data-cookie-settings]');
  if (!banner || !settings) return;
  const key = 'miblo.analytics-consent.v1';
  const lifetime = 180 * 24 * 60 * 60 * 1000;
  const enabled = /^G-[A-Z0-9]+$/.test(id) && location.hostname === 'cli.miblo.fr';
  let allowed = false;
  let loaded = false;
  let expires = 0;
  let expiryTimer;
  const disableKey = 'ga-disable-' + id;
  window[disableKey] = true;

  function remembered() {
    try {
      const saved = JSON.parse(localStorage.getItem(key));
      if (saved && typeof saved.accepted === 'boolean' && saved.expires > Date.now()
          && saved.expires <= Date.now() + lifetime) return saved;
    } catch { /* A blocked or invalid store leaves measurement off. */ }
    return null;
  }
  function pageLocation() {
    const url = new URL(location.pathname, location.origin);
    const query = new URLSearchParams(location.search);
    for (const key of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content']) {
      const value = query.get(key);
      if (value && /^[a-zA-Z0-9_-]{1,80}$/.test(value)) url.searchParams.set(key, value);
    }
    return url.href;
  }
  function clearCookies() {
    const domains = ['', location.hostname];
    for (const item of document.cookie.split(';')) {
      const name = item.split('=')[0].trim();
      if (!/^_ga(?:_|$)/.test(name)) continue;
      for (const domain of domains) document.cookie = name + '=; Max-Age=0; Path=/; SameSite=Lax'
        + (domain ? '; Domain=' + domain : '');
    }
  }
  function stop() {
    allowed = false;
    window[disableKey] = true;
    clearTimeout(expiryTimer);
    clearCookies();
  }
  function track(name, parameters = {}) {
    if (!allowed || !enabled) return;
    if (Date.now() >= expires) { stop(); banner.hidden = false; return; }
    window.gtag('event', name, { ...parameters, send_to: id });
  }
  function start() {
    allowed = true;
    if (!enabled) return;
    window[disableKey] = false;
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied'
    });
    window.gtag('js', new Date());
    let referrer = '';
    try { referrer = new URL(document.referrer).origin; } catch { /* No referrer. */ }
    window.gtag('config', id, {
      send_page_view: false, allow_google_signals: false,
      allow_ad_personalization_signals: false,
      cookie_domain: location.hostname, cookie_path: '/',
      cookie_expires: lifetime / 1000, cookie_update: false,
      page_location: pageLocation(), page_referrer: referrer
    });
    track('page_view', {page_location: pageLocation(), page_referrer: referrer, page_title: document.title});
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.append(tag);
  }
  function apply(saved) {
    expires = saved?.expires || 0;
    if (saved?.accepted) start(); else stop();
    banner.hidden = Boolean(saved);
    clearTimeout(expiryTimer);
    // Recheck on long-lived tabs without overflowing the timer's 32-bit range.
    if (saved) expiryTimer = setTimeout(refresh, Math.min(expires - Date.now() + 1, 2147483647));
  }
  function refresh() { apply(remembered()); }
  function choose(accepted) {
    const saved = {accepted, expires: Date.now() + lifetime};
    try { localStorage.setItem(key, JSON.stringify(saved)); } catch { /* This page only. */ }
    apply(saved);
    settings.focus({preventScroll: true});
  }
  banner.querySelector('[data-consent-accept]').addEventListener('click', () => choose(true));
  banner.querySelector('[data-consent-reject]').addEventListener('click', () => choose(false));
  settings.hidden = false;
  settings.addEventListener('click', () => {
    banner.hidden = false;
    banner.querySelector('[data-consent-reject]').focus({preventScroll: true});
  });
  window.addEventListener('storage', event => { if (event.key === key || event.key === null) refresh(); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden && expires && Date.now() >= expires) refresh(); });
  refresh();

  // Only named product interactions; no form values or document contents.
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (link) {
      const url = new URL(link.href, location.href);
      if (url.hostname === 'crates.io' && url.pathname === '/crates/miblo') track('install_click', {destination: 'crates_io'});
      if (url.hostname === 'github.com' && url.pathname.startsWith('/NaSuRall/Miblo/releases/')) {
        track('download_click', {file_name: url.pathname.split('/').pop(), destination: 'github_releases'});
      }
    }
  });
  document.addEventListener('miblo:install-copy', () => track('install_copy'));
  document.addEventListener('miblo:demo-start', () => track('demo_start'));
})();
