#!/usr/bin/env python3
"""Render the static site with Python's standard library. No runtime dependencies."""
import html
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STYLE_VERSION = hashlib.sha256((ROOT / 'style.css').read_bytes()).hexdigest()[:12]
sys.path.insert(0, str(ROOT))
from content.pages import PAGES

BASE = 'https://miblo.fr'
GITHUB = 'https://github.com/NaSuRall/Miblo'
CRATES = 'https://crates.io/search?q=miblo'
DEMO_GUIDES = {
    'premiere-api': ('projet', 'Voir la création dans Miblo'),
    'interface': ('post', 'Voir l’interface de Miblo'),
    'modeles': ('modeles', 'Voir l’ajout d’un modèle'),
    'relations': ('relation', 'Voir l’ajout d’une relation'),
    'migrations': ('migration', 'Voir une migration'),
    'routes': ('route', 'Voir la création d’une route'),
    'tester-les-routes': ('post', 'Voir un test POST'),
    'bases-de-donnees': ('schema', 'Voir le schéma SQLite'),
    'architecture': ('code', 'Voir l’aperçu du code'),
    'templates': ('projet', 'Voir la création avec les templates'),
}


def header(prefix, docs=False):
    return f'''<a class="skip-link" href="#contenu">Aller au contenu</a>
<header class="site-header"><div class="header-inner">
  <a class="brand" href="{prefix}index.html" aria-label="Miblo, accueil"><img class="brand-logo" src="{prefix}assets/miblo-logo.svg" width="350" height="102" alt=""></a>
  <nav class="main-nav" aria-label="Navigation principale">
    <a href="{prefix}index.html" {'aria-current="page"' if not docs else ''}>Démo</a>
    <a href="{prefix}docs/index.html" {'aria-current="true"' if docs else ''}>Documentation</a>
  </nav>
  <div class="header-actions"><a class="github-link" href="{GITHUB}">GitHub <span aria-hidden="true">↗</span></a><button class="search-trigger" data-search-open aria-label="Rechercher dans la documentation" hidden><span>Rechercher</span><kbd>/</kbd></button></div>
</div></header>'''


def footer(prefix):
    return f'''<footer class="site-footer"><div class="footer-main"><a class="brand" href="{prefix}index.html" aria-label="Miblo, retour à l’accueil"><img class="brand-logo" src="{prefix}assets/miblo-logo.svg" width="350" height="102" alt=""></a><div class="footer-links"><a href="{prefix}docs/index.html">Documentation</a><a href="{GITHUB}">GitHub ↗</a><a href="{CRATES}">crates.io ↗</a><a href="https://github.com/NaSuRall/miblo_templates/releases">Templates ↗</a></div></div><div class="footer-bottom"><span>Open source · MIT · Conçu par NaSuRall</span><span>Rust / Axum / SQLx</span></div></footer>'''


SEARCH = '''<dialog class="search-dialog" aria-labelledby="search-title"><div class="search-head"><label id="search-title" for="search-input"><span class="blue">/</span> Rechercher dans la doc</label><button class="text-button" data-search-close aria-label="Fermer la recherche">Échap ×</button></div><input id="search-input" type="search" placeholder="Modèle, SQLite, migration…" autocomplete="off" spellcheck="false" aria-controls="search-results"><p id="search-status" class="search-status" role="status">Rechercher une fonctionnalité ou une commande.</p><div id="search-results" class="search-results"></div><div class="search-help">↑ ↓ parcourir <span>Entrée ouvrir</span></div></dialog><div class="toast" role="status" aria-live="polite"></div>'''


def page(title, description, body, path, prefix='', docs=False):
    demo_script = '<link rel="stylesheet" href="../docs.css">' if docs else '<link rel="stylesheet" href="demo.css"><link rel="stylesheet" href="assets/miblo-demo.css"><script defer src="demo.js"></script>'
    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(description, quote=True)}"><meta name="theme-color" content="#0c0e12"><meta name="color-scheme" content="dark"><link rel="canonical" href="{BASE}/{path}"><meta property="og:type" content="website"><meta property="og:site_name" content="Miblo"><meta property="og:locale" content="fr_FR"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{BASE}/{path}"><meta name="twitter:card" content="summary"><link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}style.css?v={STYLE_VERSION}"><script defer src="{prefix}app.js"></script>{demo_script}</head><body class="{'docs-page' if docs else 'home-page'}">{header(prefix, docs)}{body}{footer(prefix)}{SEARCH}</body></html>'''


def sidebar(current):
    out = ['<aside class="docs-sidebar"><details class="docs-menu" open><summary>Parcourir la documentation <span>+</span></summary><nav aria-label="Chapitres de documentation">']
    group = None
    for p in PAGES:
        if p['group'] != group:
            if group is not None: out.append('</ul>')
            group = p['group']
            out.append(f'<p class="nav-group">{html.escape(group)}</p><ul>')
        active = ' aria-current="page"' if p['slug'] == current else ''
        out.append(f'<li><a href="{p["slug"]}.html"{active}><span aria-hidden="true">{">" if active else "·"}</span> {html.escape(p["title"])}</a></li>')
    out.append('</ul></nav><a class="sidebar-source" href="https://github.com/NaSuRall/Miblo">Code source ↗</a></details></aside>')
    return ''.join(out)


def plain(value):
    value = re.sub(r'<div class="code-header">.*?</div>', '', value, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value))).strip()


def recording_poster():
    recording = json.loads((ROOT / 'assets/miblo-demo.json').read_text())
    ansi = dict(black='#000000', red='#cd0000', green='#00cd00', brown='#cdcd00',
                blue='#0000ee', magenta='#cd00cd', cyan='#00cdcd', white='#e5e5e5')
    def color(value, default):
        if value == 'default': return default
        if re.fullmatch('[0-9a-f]{6}', value): return '#' + value
        return ansi[value]
    rules = ['/* Generated from the real terminal recording. */']
    for i, (fg, bg, bold, italic, underline, reverse) in enumerate(recording['styles']):
        fg, bg = color(fg, '#e0e6f5'), color(bg, '#0f121d')
        if reverse: fg, bg = bg, fg
        rules.append(f'.terminal-style-{i} {{ color: {fg}; background: {bg}; font-weight: {700 if bold else 400}; font-style: {"italic" if italic else "normal"}; text-decoration: {"underline" if underline else "none"}; }}')
    (ROOT / 'assets/miblo-demo.css').write_text('\n'.join(rules) + '\n')
    return ''.join('<span class="terminal-row">' + ''.join(
        f'<span class="terminal-style-{style}">{html.escape(text)}</span>'
        for style, text in row) + '</span>' for row in recording['frames'][0]['rows'])


def main():
    home = (ROOT / 'content/home.html').read_text().replace('<!-- DEMO_POSTER -->', recording_poster())
    (ROOT / 'index.html').write_text(page('Miblo — Générateur d’API Rust', 'Générez des modèles, des routes CRUD et des migrations SQL depuis le terminal. Rust, Axum, SQLx, SQLite ou MySQL. Démo et documentation.', home, ''))
    search = []
    paths = ['']
    for i, p in enumerate(PAGES):
        toc = ''.join(f'<li><a href="#{s["id"]}">{html.escape(s["title"])}</a></li>' for s in p['sections'])
        sections = ''.join(f'<section class="doc-section" id="{s["id"]}"><h2>{html.escape(s["title"])}</h2>{s["body"]}</section>' for s in p['sections'])
        prev = f'<a href="{PAGES[i-1]["slug"]}.html"><span>← Précédent</span>{html.escape(PAGES[i-1]["title"])}</a>' if i else '<span></span>'
        nxt = f'<a href="{PAGES[i+1]["slug"]}.html"><span>Suivant →</span>{html.escape(PAGES[i+1]["title"])}</a>' if i + 1 < len(PAGES) else '<a href="../index.html"><span>Retour →</span>Voir la démo</a>'
        demo = DEMO_GUIDES.get(p['slug'])
        demo_link = f'<a class="doc-demo-link" href="../index.html?demo={demo[0]}#demo">▶ {demo[1]} <span aria-hidden="true">→</span></a>' if demo else ''
        body = f'''<div class="docs-layout">{sidebar(p['slug'])}<main class="doc-content" id="contenu"><div class="breadcrumb">~/miblo/docs/<span>{p['slug'] if p['slug'] != 'index' else 'bienvenue'}</span></div><div class="doc-heading"><h1>{html.escape(p['title'])}</h1><p class="lead">{html.escape(p['intro'])}</p>{demo_link}</div>{sections}<nav class="doc-pagination" aria-label="Pages précédente et suivante">{prev}{nxt}</nav><p class="doc-feedback"><a href="{GITHUB}/issues">Signaler une erreur dans cette page ↗</a></p></main><aside class="docs-toc"><p>Dans cette page</p><nav aria-label="Sommaire de la page"><ul>{toc}</ul></nav><div class="doc-version"><span class="status-dot"></span> Documentation 0.9.0<br><span>Templates 0.6.0</span></div></aside></div>'''
        path = f'docs/{p["slug"]}.html'
        (ROOT / path).write_text(page(f'{p["title"]} — Documentation Miblo', p['intro'], body, path, '../', True))
        paths.append(path)
        search.append({'title': p['title'], 'section': 'Vue d’ensemble', 'url': path, 'text': p['intro']})
        for s in p['sections']:
            search.append({'title': p['title'], 'section': s['title'], 'url': path + '#' + s['id'], 'text': plain(s['body'])})
    (ROOT / 'search-index.json').write_text(json.dumps(search, ensure_ascii=False, separators=(',', ':')))
    urls = ''.join(f'<url><loc>{BASE}/{path}</loc></url>' for path in paths)
    (ROOT / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    print(f'Built home + {len(PAGES)} documentation pages, search index and sitemap.')


if __name__ == '__main__':
    main()
