// Execute the real tracking script in an isolated DOM stub: no network or browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../analytics.js'), 'utf8');
const id = 'G-TEST123';
const key = 'miblo.analytics-consent.v1';
function setup({saved, blocked = false, hostname = 'cli.miblo.fr'} = {}) {
  const stored = new Map(saved ? [[key, saved]] : []);
  const listeners = {};
  const appended = [];
  const cookies = [];
  const nodes = {};
  for (const name of ['banner','settings','accept','reject']) nodes[name] = {
    hidden: true, addEventListener(event, fn) { this[event] = fn; }, focus() {}
  };
  nodes.banner.querySelector = selector => selector.includes('accept') ? nodes.accept : nodes.reject;
  const document = {
    currentScript: {dataset: {measurementId: id}},
    referrer: 'https://www.linkedin.com/feed/?private=secret',
    title: 'Miblo', hidden: false,
    querySelector: selector => selector.includes('banner') ? nodes.banner : nodes.settings,
    createElement: () => ({}), head: {append(tag) { appended.push(tag); }},
    addEventListener(name, fn) { listeners[name] = fn; },
    get cookie() { return '_ga=old; _ga_TEST123=old; unrelated=keep'; },
    set cookie(value) { cookies.push(value); }
  };
  const window = {addEventListener(name, fn) { listeners[name] = fn; }};
  const location = new URL('https://' + hostname + '/fr/?utm_source=linkedin&utm_medium=social&utm_campaign=beta_091&email=private@example.com&utm_content=bad%40example.com#secret');
  const context = {document, window, location, URL, URLSearchParams, Date,
    setTimeout() { return 1; }, clearTimeout() {},
    localStorage: {
      getItem(k) { if (blocked) throw Error('blocked'); return stored.get(k) || null; },
      setItem(k,v) { if (blocked) throw Error('blocked'); stored.set(k,v); }
    }
  };
  vm.runInNewContext(source, context);
  return {nodes,window,listeners,appended,cookies,stored,
    events: () => (window.dataLayer || []).map(v=>Array.from(v)).filter(v=>v[0]==='event')};
}
const fresh = setup();
assert.equal(fresh.appended.length, 0);
assert.equal(fresh.nodes.banner.hidden, false);
fresh.nodes.reject.click();
assert.equal(fresh.appended.length, 0);
assert.equal(fresh.nodes.banner.hidden, true);
fresh.nodes.settings.click();
assert.equal(fresh.nodes.banner.hidden, false);
fresh.nodes.accept.click();
assert.equal(fresh.appended.length, 1);
assert.equal(fresh.appended[0].src, 'https://www.googletagmanager.com/gtag/js?id=' + id);
assert.equal(fresh.events().filter(e=>e[1]==='page_view').length, 1);
const view = fresh.events()[0][2];
assert.equal(view.page_location, 'https://cli.miblo.fr/fr/?utm_source=linkedin&utm_medium=social&utm_campaign=beta_091');
assert.equal(view.page_referrer, 'https://www.linkedin.com');
fresh.listeners['miblo:demo-start']();
assert.equal(fresh.events().at(-1)[1], 'demo_start');
fresh.nodes.reject.click();
const count = fresh.events().length;
fresh.listeners['miblo:demo-start']();
assert.equal(fresh.events().length, count);
assert.equal(fresh.window['ga-disable-' + id], true);
assert.ok(fresh.cookies.every(c=>!c.startsWith('unrelated=')));
assert.ok(fresh.cookies.some(c=>c.startsWith('_ga=')));
fresh.nodes.accept.click();
assert.equal(fresh.appended.length, 1, 'never load a second Google tag');
fresh.stored.delete(key);
fresh.listeners.storage({key});
assert.equal(fresh.window['ga-disable-' + id], true);
assert.equal(fresh.nodes.banner.hidden, false);
for (const saved of ['broken', JSON.stringify({accepted:true, expires:Date.now()-1000}), JSON.stringify({accepted:'yes',expires:Date.now()+10000})]) {
  assert.equal(setup({saved}).appended.length, 0);
}
const consent = JSON.stringify({accepted:true, expires:Date.now()+10000});
assert.equal(setup({saved:consent}).appended.length, 1);
assert.equal(setup({saved:consent,hostname:'localhost'}).appended.length, 0);
const denied = JSON.stringify({accepted:false,expires:Date.now()+10000});
assert.equal(setup({saved:denied}).nodes.banner.hidden,true);
const blocked = setup({blocked:true});
assert.equal(blocked.appended.length,0);
blocked.nodes.accept.click();
assert.equal(blocked.appended.length,1);
console.log('PASS: analytics opt-in, refusal, withdrawal, persistence, expiry, storage failure, cross-tab withdrawal, sanitized URLs and local-preview isolation.');
