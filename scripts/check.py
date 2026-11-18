#!/usr/bin/env python3
"""Check links, anchors, document metadata and search destinations without dependencies."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
import unicodedata

ROOT = Path(__file__).resolve().parents[1]

class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links, self.errors = path, set(), [], []
        self.h1 = 0
        self.description = False
        self.canonical = False
        self.lang = False
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids: self.errors.append('Duplicate id: ' + a['id'])
            self.ids.add(a['id'])
        self.h1 += tag == 'h1'
        self.description |= tag == 'meta' and a.get('name') == 'description' and bool(a.get('content'))
        self.canonical |= tag == 'link' and a.get('rel') == 'canonical' and a.get('href', '').startswith('https://miblo.fr/')
        self.lang |= tag == 'html' and a.get('lang') == 'fr'
        if tag in ('a', 'link') and a.get('href'): self.links.append(a['href'])
        if tag in ('script', 'img') and a.get('src'): self.links.append(a['src'])

def main():
    paths = [ROOT / 'index.html', *sorted((ROOT / 'docs').glob('*.html'))]
    documents = {p.resolve(): Document(p) for p in paths}
    errors = []
    checked = 0
    recording = json.loads((ROOT / 'assets/miblo-demo.json').read_text())
    demo_chapters = {
        ''.join(c for c in unicodedata.normalize('NFD', chapter['title']) if not unicodedata.combining(c)).lower()
        for chapter in recording['chapters']
    }
    def check_link(source, href):
        nonlocal checked
        url = urlsplit(href)
        if url.scheme or url.netloc: return
        target = ((ROOT if url.path.startswith('/') else source.parent) / unquote(url.path).lstrip('/')).resolve() if url.path else source.resolve()
        if target.is_dir(): target /= 'index.html'
        checked += 1
        if not target.is_relative_to(ROOT) or not target.is_file():
            errors.append(f'{source.relative_to(ROOT)}: missing file {href}')
        elif url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids:
            errors.append(f'{source.relative_to(ROOT)}: missing anchor {href}')
        if target == ROOT / 'index.html' and 'demo' in parse_qs(url.query):
            for chapter in parse_qs(url.query)['demo']:
                if chapter not in demo_chapters:
                    errors.append(f'{source.relative_to(ROOT)}: unknown demo chapter {chapter}')
    for path, doc in documents.items():
        if doc.h1 != 1: doc.errors.append(f'Expected one h1, got {doc.h1}')
        if not doc.description: doc.errors.append('Missing description')
        if not doc.canonical: doc.errors.append('Missing canonical URL')
        if not doc.lang: doc.errors.append('Missing French lang attribute')
        errors.extend(f'{path.relative_to(ROOT)}: {e}' for e in doc.errors)
        for href in doc.links: check_link(path, href)
    entries = json.loads((ROOT / 'search-index.json').read_text())
    for item in entries:
        if not all(item.get(k) for k in ('title', 'section', 'text', 'url')):
            errors.append('Incomplete search entry: ' + repr(item))
        check_link(ROOT / 'index.html', item['url'])
    if errors: raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(documents)} pages; {checked} local links/anchors; {len(entries)} search entries; metadata and unique IDs.')

if __name__ == '__main__':
    main()
