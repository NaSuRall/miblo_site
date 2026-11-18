(() => {
  'use strict';
  const demo = document.getElementById('demo');
  if (!demo) return;
  const url = new URL(demo.dataset.recording, document.baseURI);
  const en = document.documentElement.lang === 'en';
  const translations = en ? fetch(new URL(demo.dataset.demoLabels, document.baseURI)).then(response => {
    if (!response.ok) throw new Error('translations unavailable');
    return response.json();
  }) : Promise.resolve({});
  const t = (fr, english) => en ? english : fr;
  const byId = id => document.getElementById(id);
  const terminal = byId('demo-terminal');
  const play = byId('demo-play');
  const progress = byId('demo-progress');
  const caption = byId('demo-caption');
  let recording, index = 0, playing = false, timer;
  let offsets = [], total = 0, chapterButtons = [];
  const time = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;

  function playback() {
    play.textContent = playing ? 'Ⅱ Pause' : t('▶ Lire la démo', '▶ Play demo');
    play.setAttribute('aria-pressed', String(playing));
    caption.setAttribute('aria-live', playing ? 'off' : 'polite');
  }
  function pause() {
    clearTimeout(timer);
    playing = false;
    playback();
  }
  function render() {
    const frame = recording.frames[index];
    const fragment = document.createDocumentFragment();
    for (const runs of frame.rows) {
      const row = document.createElement('span');
      row.className = 'terminal-row';
      for (const [style, text] of runs) {
        const span = document.createElement('span');
        span.className = `terminal-style-${style}`;
        span.textContent = text;
        row.append(span);
      }
      fragment.append(row);
    }
    terminal.replaceChildren(fragment);
    caption.textContent = frame.caption;
    byId('demo-key').textContent = frame.key;
    byId('demo-key').hidden = !frame.key;
    progress.value = index;
    progress.setAttribute('aria-valuetext', `${time(offsets[index])} : ${frame.caption}`);
    byId('demo-time').textContent = `${time(index === recording.frames.length - 1 ? total : offsets[index])} / ${time(total)}`;
    byId('demo-previous').disabled = index === 0;
    byId('demo-next').disabled = index === recording.frames.length - 1;
    chapterButtons.forEach((button, i) => {
      const active = index >= recording.chapters[i].frame &&
        (i === chapterButtons.length - 1 || index < recording.chapters[i + 1].frame);
      button.setAttribute('aria-pressed', String(active));
    });
  }
  function seek(next) {
    pause();
    index = Math.max(0, Math.min(next, recording.frames.length - 1));
    render();
  }
  function schedule() {
    timer = setTimeout(() => {
      if (index === recording.frames.length - 1) { pause(); return; }
      index++;
      render();
      schedule();
    }, recording.frames[index].seconds * 1000);
  }
  play.addEventListener('click', () => {
    if (playing) { pause(); return; }
    if (index === recording.frames.length - 1) { index = 0; render(); }
    playing = true;
    document.dispatchEvent(new Event('miblo:demo-start'));
    playback();
    schedule();
  });
  byId('demo-previous').addEventListener('click', () => seek(index - 1));
  byId('demo-next').addEventListener('click', () => seek(index + 1));
  byId('demo-reset').addEventListener('click', () => seek(0));
  progress.addEventListener('input', () => seek(Number(progress.value)));
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { if (!entries[0].isIntersecting) pause(); }).observe(demo);
  }
  // A native dialog also works in embedded browsers without Fullscreen API access.
  const expand = byId('demo-fullscreen');
  const modal = document.createElement('dialog');
  modal.className = 'record-modal';
  modal.setAttribute('aria-label', t('Démonstration Miblo agrandie', 'Expanded Miblo demo'));
  const position = document.createComment('demo position');
  demo.before(position);
  document.body.append(modal);
  expand.hidden = false;
  let previousOverflow;
  expand.addEventListener('click', () => {
    if (modal.open) { modal.close(); return; }
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    modal.append(demo);
    expand.textContent = t('Réduire ⛶', 'Collapse ⛶');
    modal.showModal();
    expand.focus();
  });
  modal.addEventListener('close', () => {
    position.after(demo);
    document.body.style.overflow = previousOverflow;
    expand.textContent = t('Agrandir ⛶', 'Expand ⛶');
    expand.focus();
  });
  Promise.all([fetch(url).then(response => {
    if (!response.ok) throw new Error('recording unavailable');
    return response.json();
  }), translations]).then(([data, labels]) => {
    if (data.version !== 1 || !data.frames?.length || !data.chapters?.length) throw new Error('invalid recording');
    recording = data;
    for (const frame of recording.frames) {
      frame.caption = labels[frame.caption] || frame.caption;
      frame.key = labels[frame.key] || frame.key;
    }
    const requestedChapter = new URLSearchParams(window.location.search).get('demo');
    const chapterSlug = title => title.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const requested = recording.chapters.find(chapter => chapterSlug(chapter.title) === requestedChapter);
    if (requested) index = requested.frame;
    offsets = recording.frames.map(frame => { const offset = total; total += frame.seconds; return offset; });
    progress.max = recording.frames.length - 1;
    chapterButtons = recording.chapters.map(chapter => {
      const button = document.createElement('button');
      button.textContent = labels[chapter.title] || chapter.title;
      button.addEventListener('click', () => seek(chapter.frame));
      byId('demo-chapters').append(button);
      return button;
    });
    render();
    byId('demo-controls').hidden = false;
    byId('demo-chapters').hidden = false;
  }).catch(() => {
    caption.textContent = t('Enregistrement indisponible. Rechargez la page ou consultez la documentation.', 'Recording unavailable. Reload the page or browse the documentation.');
  });
})();
