(() => {
  'use strict';
  const script = document.currentScript;
  const root = new URL('.', script.src);
  const en = document.documentElement.lang === 'en';
  const t = (fr, english) => en ? english : fr;
  function updateLanguageLinks() { document.querySelectorAll('[data-language]').forEach(link => {
    const target = new URL(link.href);
    target.hash = window.location.hash;
    const chapter = new URLSearchParams(window.location.search).get('demo');
    if (chapter) target.searchParams.set('demo', chapter);
    link.href = target.href;
  }); }
  updateLanguageLinks();
  window.addEventListener('hashchange', updateLanguageLinks);
  const toast = document.querySelector('.toast');
  let toastTimer;
  function announce(message) {
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('visible');
    toastTimer = setTimeout(() => toast.classList.remove('visible'), 3000);
  }

  // Reading and navigation remain available without JavaScript.
  document.querySelectorAll('[data-copy]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const block = button.closest('.code-block').querySelector('code');
      const value = block.textContent;
      let copied = false;
      try {
        await navigator.clipboard.writeText(value);
        copied = true;
      } catch {
        const input = document.createElement('textarea');
        input.value = value;
        input.setAttribute('aria-hidden', 'true');
        Object.assign(input.style, {position: 'fixed', opacity: '0', top: '0'});
        document.body.append(input);
        input.select();
        try { copied = document.execCommand('copy'); } catch { /* Offer manual selection below. */ }
        input.remove();
        button.focus();
      }
      if (copied) {
        button.textContent = t('Copié ✓', 'Copied ✓');
        announce(t('Commande copiée.', 'Command copied.'));
        setTimeout(() => { button.textContent = t('Copier', 'Copy'); }, 2000);
      } else {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(block);
        selection.removeAllRanges();
        selection.addRange(range);
        announce(t('Copie indisponible. Le texte est sélectionné : utilisez Ctrl/Cmd + C.', 'Copy unavailable. The text is selected: use Ctrl/Cmd + C.'));
      }
    });
  });
  document.querySelectorAll('.code-block pre, .code-diff').forEach(pre => {
    pre.tabIndex = 0;
    pre.setAttribute('aria-label', t('Exemple de code, défilement horizontal possible', 'Code example; horizontal scrolling available'));
  });


  const menu = document.querySelector('.docs-menu');
  const narrow = window.matchMedia('(max-width: 640px)');
  function resizeMenu() { if (menu) menu.open = !narrow.matches; }
  resizeMenu();
  narrow.addEventListener('change', resizeMenu);

  const tocLinks = [...document.querySelectorAll('.docs-toc a')];
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        tocLinks.forEach(link => {
          if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      }
    }, {rootMargin: '-100px 0px -65% 0px'});
    document.querySelectorAll('.doc-section').forEach(section => observer.observe(section));
  }

  const dialog = document.querySelector('.search-dialog');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  let indexPromise;
  let revision = 0;
  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(new URL(document.body.dataset.searchIndex, document.baseURI))
        .then(response => {
          if (!response.ok) throw new Error('Search index unavailable');
          return response.json();
        })
        .catch(error => { indexPromise = null; throw error; });
    }
    return indexPromise;
  }
  async function search() {
    const ownRevision = ++revision;
    status.textContent = t('Chargement de la documentation…', 'Loading documentation…');
    try {
      const items = await loadIndex();
      if (ownRevision !== revision) return;
      const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
      const matches = items.map(item => {
        const title = normalize(item.title);
        const section = normalize(item.section);
        const text = normalize(item.text);
        const all = title + ' ' + section + ' ' + text;
        const score = terms.every(term => all.includes(term))
          ? terms.reduce((sum, term) => sum + (title.includes(term) ? 8 : 0) + (section.includes(term) ? 5 : 0) + (text.includes(term) ? 1 : 0), 0)
          : -1;
        return {item, score};
      }).filter(({item, score}) => terms.length ? score >= 0 : item.overview === true)
        .sort((a, b) => b.score - a.score);
      results.replaceChildren();
      matches.slice(0, 8).forEach(({item}) => {
        const link = document.createElement('a');
        link.className = 'search-result';
        link.href = new URL(item.url, root).href;
        const label = document.createElement('span');
        label.textContent = item.title;
        const title = document.createElement('strong');
        title.textContent = item.section;
        const excerpt = document.createElement('p');
        const position = terms.length ? Math.max(0, normalize(item.text).indexOf(terms[0]) - 25) : 0;
        const fragment = item.text.slice(position, position + 145);
        excerpt.textContent = (position ? '…' : '') + fragment + (position + 145 < item.text.length ? '…' : '');
        link.append(label, title, excerpt);
        results.append(link);
      });
      status.textContent = !terms.length ? t('Parcourir la documentation', 'Browse documentation')
        : matches.length ? matches.length + t(' résultat', ' result') + (matches.length > 1 ? 's' : '') + (matches.length > 8 ? t(' · 8 affichés', ' · showing 8') : '')
          : t('Aucun résultat. Essayez « modèle », « SQLite » ou « migration ».', 'No results. Try “model”, “SQLite” or “migration”.');
    } catch {
      if (ownRevision !== revision) return;
      results.replaceChildren();
      status.textContent = t('Recherche indisponible. La documentation reste accessible :', 'Search unavailable. You can still browse the documentation:');
      const link = document.createElement('a');
      link.className = 'search-result';
      link.href = new URL(document.body.dataset.docsHome, document.baseURI).href;
      link.textContent = t('Ouvrir le sommaire de la documentation →', 'Open documentation contents →');
      results.append(link);
    }
  }
  function openSearch() {
    if (!dialog.open) dialog.showModal();
    input.focus();
    search();
  }
  document.querySelectorAll('[data-search-open]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', openSearch);
  });
  document.querySelector('[data-search-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  input.addEventListener('input', search);
  results.addEventListener('click', event => {
    // A result may point to an anchor in the current page, without a reload.
    if (event.target.closest('a')) dialog.close();
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      // Search inputs can consume Escape to clear their value before the dialog.
      event.preventDefault();
      event.stopPropagation();
      dialog.close();
      return;
    }
    const links = [...results.querySelectorAll('a')];
    const current = links.indexOf(document.activeElement);
    if (event.key === 'ArrowDown' && links.length) {
      event.preventDefault();
      links[(current + 1) % links.length].focus();
    } else if (event.key === 'ArrowUp' && links.length) {
      event.preventDefault();
      if (current === 0) input.focus();
      else links[current < 0 ? links.length - 1 : current - 1].focus();
    } else if (event.key === 'Enter' && document.activeElement === input && links.length) {
      event.preventDefault();
      links[0].click();
    }
  });
  document.addEventListener('keydown', event => {
    const editing = event.target.closest('input, textarea, select, [contenteditable="true"]');
    const commandK = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k';
    if (commandK || (event.key === '/' && !editing && !event.ctrlKey && !event.metaKey && !event.altKey)) {
      event.preventDefault();
      openSearch();
    }
  });
})();
