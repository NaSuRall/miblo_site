#!/usr/bin/env python3
"""Validate bilingual pages, links, search, structured data and SEO contracts."""
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
import sys
from urllib.parse import parse_qs, unquote, urlsplit
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.build import BASE, PAGES, canonical, page_path


class Document(HTMLParser):
    def __init__(self,path):
        super().__init__()
        self.path,self.ids,self.links,self.errors = path,set(),[],[]
        self.h1,self.lang,self.title,self.json_text = 0,None,'',''
        self.meta,self.alternates,self.switches = {},{},{}
        self.canonical = None
        self.in_title = self.in_json = False
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self,tag,attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids: self.errors.append('Duplicate id: '+a['id'])
            self.ids.add(a['id'])
        if tag=='html': self.lang=a.get('lang')
        if tag=='h1': self.h1+=1
        if tag=='title': self.in_title=True
        if tag=='script' and a.get('type')=='application/ld+json': self.in_json=True
        if tag=='meta': self.meta[a.get('name',a.get('property'))]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a.get('href')
        if tag=='link' and a.get('rel')=='alternate': self.alternates[a.get('hreflang')]=a.get('href')
        if tag=='a' and a.get('data-language'): self.switches[a['data-language']]=a.get('href')
        if tag in ('a','link') and a.get('href'): self.links.append(a['href'])
        if tag in ('script','img') and a.get('src'): self.links.append(a['src'])
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
        if tag=='script': self.in_json=False
    def handle_data(self,data):
        if self.in_title: self.title+=data
        if self.in_json: self.json_text+=data


def main():
    expected = {page_path(lang,key):(lang,key) for lang,pages in PAGES.items() for key in [None,*[p['slug'] for p in pages]]}
    documents = {(ROOT/path).resolve():Document(ROOT/path) for path in expected}
    errors=[]
    checked=0
    recording=json.loads((ROOT/'assets/miblo-demo.json').read_text())
    chapters={''.join(c for c in unicodedata.normalize('NFD',ch['title']) if not unicodedata.combining(c)).lower() for ch in recording['chapters']}
    def target_path(source,href):
        url=urlsplit(href)
        if url.netloc and url.netloc!=urlsplit(BASE).netloc: return None
        if url.scheme and url.scheme not in ('http','https'): return None
        target=(ROOT/unquote(url.path).lstrip('/')) if url.path.startswith('/') else source.parent/unquote(url.path)
        if not url.path: target=source
        target=target.resolve()
        if target.is_dir() or url.path.endswith('/'): target/='index.html'
        return target
    def check_link(source,href):
        nonlocal checked
        target=target_path(source,href)
        if target is None: return
        checked+=1
        url=urlsplit(href)
        if not target.is_relative_to(ROOT) or not target.is_file(): errors.append(f'{source.relative_to(ROOT)}: missing file {href}')
        elif url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids: errors.append(f'{source.relative_to(ROOT)}: missing anchor {href}')
        if 'demo' in parse_qs(url.query):
            if target not in {ROOT/page_path('en'),ROOT/page_path('fr')}: errors.append('Demo link outside home: '+href)
            if any(v not in chapters for v in parse_qs(url.query)['demo']): errors.append('Unknown demo chapter: '+href)
    titles=set()
    descriptions=set()
    for path,doc in documents.items():
        relative=str(path.relative_to(ROOT))
        lang,key=expected[relative]
        if doc.h1!=1: doc.errors.append(f'Expected one h1, got {doc.h1}')
        if doc.lang!=lang: doc.errors.append('Wrong document language')
        if doc.canonical!=canonical(relative): doc.errors.append('Wrong canonical URL')
        if not doc.title or doc.title in titles: doc.errors.append('Missing/duplicate title')
        titles.add(doc.title)
        description=doc.meta.get('description')
        if not description or description in descriptions: doc.errors.append('Missing/duplicate description')
        descriptions.add(description)
        if doc.meta.get('robots')!='index,follow,max-image-preview:large': doc.errors.append('Unexpected indexing policy')
        expected_alternates={code:canonical(page_path(code,key)) for code in ('en','fr')}
        expected_alternates['x-default']=expected_alternates['en']
        if doc.alternates!=expected_alternates: doc.errors.append('Incomplete/wrong hreflang cluster')
        for code in ('en','fr'):
            if target_path(path,doc.switches.get(code,''))!=ROOT/page_path(code,key): doc.errors.append('Wrong language switch destination')
        for name in ('og:title','og:description','og:url','og:image','og:image:alt','twitter:card','twitter:image'):
            if not doc.meta.get(name): doc.errors.append('Missing metadata: '+name)
        if doc.meta.get('og:url')!=doc.canonical: doc.errors.append('Open Graph URL differs from canonical')
        check_link(path,doc.meta.get('og:image',''))
        try:
            graph=json.loads(doc.json_text)['@graph']
            article=next(x for x in graph if x.get('@type') in ('WebPage','TechArticle'))
            if article['url']!=doc.canonical or article['inLanguage']!=lang: doc.errors.append('Structured data language/URL mismatch')
            if key is not None and not any(x['@type']=='BreadcrumbList' for x in graph): doc.errors.append('Missing breadcrumb schema')
        except (ValueError,KeyError,StopIteration): doc.errors.append('Invalid structured data')
        errors.extend(f'{relative}: {e}' for e in doc.errors)
        for href in doc.links: check_link(path,href)
    for french,english in zip(PAGES['fr'],PAGES['en']):
        if french['slug']!=english['slug'] or [s['id'] for s in french['sections']]!=[s['id'] for s in english['sections']]: errors.append('Translation page/section mismatch: '+french['slug'])
    entries_count=0
    for lang in ('en','fr'):
        entries=json.loads((ROOT/('search-index.json' if lang=='en' else 'fr/search-index.json')).read_text())
        entries_count+=len(entries)
        for item in entries:
            if not all(item.get(k) for k in ('title','section','text','url')): errors.append('Incomplete search entry')
            target=target_path(ROOT/'index.html',item['url'])
            if target not in documents or documents[target].lang!=lang: errors.append('Search result in wrong language: '+item['url'])
            check_link(ROOT/'index.html',item['url'])
        png=(ROOT/f'assets/social-{lang}.png').read_bytes()
        if png[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',png[16:24])!=(1200,630): errors.append('Invalid social card: '+lang)
    labels=json.loads((ROOT/'assets/demo-en.json').read_text())
    for frame in recording['frames']:
        if not labels.get(frame['caption']): errors.append('Missing English caption: '+frame['caption'])
    sitemap=ET.parse(ROOT/'sitemap.xml')
    urls=[loc.text for loc in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    if len(urls)!=len(expected) or set(urls)!={canonical(p) for p in expected}: errors.append('Sitemap does not cover canonical pages exactly')
    if f'Sitemap: {BASE}/sitemap.xml' not in (ROOT/'robots.txt').read_text(): errors.append('Wrong robots sitemap')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(documents)} bilingual pages; {checked} local links; {entries_count} search entries; canonical/hreflang, structured data, social cards and sitemap.')


if __name__=='__main__': main()
