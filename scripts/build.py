#!/usr/bin/env python3
"""Build both languages as static HTML, with localized search and SEO metadata."""
import hashlib
import html
import json
from pathlib import Path
import posixpath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content.pages import PAGES as FR
from content.pages_en import PAGES as EN
from content.locales import SLUGS, TEXT
from content.downloads import VERSION, RELEASE

BASE = 'https://cli.miblo.fr'
GITHUB = 'https://github.com/NaSuRall/Miblo'
CRATES = 'https://crates.io/crates/miblo'
# Public ownership proof for the site's existing owner's Search Console account.
GOOGLE_VERIFICATION = 'iTdcU0Bbpn9YEbI9BMKEY61hM8QU_BVbs59WiKIqeJw'
PAGES = {'en': EN, 'fr': FR}
DEMO_GUIDES = {'premiere-api':'projet','interface':'langue','modeles':'modeles','relations':'relation','migrations':'migration','routes':'route','tester-les-routes':'post','bases-de-donnees':'schema','architecture':'code','templates':'projet'}


def page_path(lang, key=None):
    if key is None: return 'index.html' if lang == 'en' else 'fr/index.html'
    return f'en/docs/{SLUGS[key]}.html' if lang == 'en' else f'docs/{key}.html'


def canonical(path):
    return BASE + '/' + (path[:-10] if path.endswith('index.html') else path)


def relative(current, target):
    link = posixpath.relpath(target, posixpath.dirname(current) or '.')
    return (link[:-10] or './') if link.endswith('index.html') else link


def asset(current, target):
    digest = hashlib.sha256((ROOT / target).read_bytes()).hexdigest()[:12]
    return relative(current, target) + '?v=' + digest


def localized_links(body, lang, current, home=False):
    def replace(match):
        attr, value = match.groups()
        if value.startswith(('http:', 'https:', '#', 'mailto:')): return match.group(0)
        path, separator, fragment = value.partition('#')
        if path.startswith('assets/'):
            path = relative(current, path)
        elif home and path.startswith('docs/'):
            key = path.removeprefix('docs/').removesuffix('.html')
            path = relative(current, page_path(lang, key))
        elif not home and path.endswith('.html') and '/' not in path:
            key = path.removesuffix('.html')
            if key in SLUGS: path = relative(current, page_path(lang, key))
        return f'{attr}="{path}{separator}{fragment}"'
    return re.sub(r'(href|src)="([^"]+)"', replace, body)


def language_switch(lang, current, key):
    links = []
    for code, label in [('en', 'English'), ('fr', 'Français')]:
        active = ' aria-current="page"' if code == lang else ''
        links.append(f'<a href="{relative(current, page_path(code, key))}" lang="{code}" hreflang="{code}" data-language="{code}" aria-label="{label}"{active}>{code.upper()}</a>')
    return f'<nav class="language-switch" aria-label="{TEXT[lang]["language"]}">' + ''.join(links) + '</nav>'


def header(lang, current, key):
    t = TEXT[lang]
    home, docs = (relative(current, page_path(lang, item)) for item in (None, 'index'))
    return f'''<a class="skip-link" href="#contenu">{t['skip']}</a>
<header class="site-header"><div class="header-inner">
<a class="brand" href="{home}" aria-label="{t['home']}"><img class="brand-logo" src="{relative(current, 'assets/miblo-logo.svg')}" width="350" height="102" alt=""></a>
<nav class="main-nav" aria-label="{t['nav']}"><a href="{home}" {'aria-current="page"' if key is None else ''}>{t['demo']}</a><a href="{docs}" {'aria-current="true"' if key is not None else ''}>Documentation</a></nav>
<div class="header-actions">{language_switch(lang,current,key)}<a class="github-link" href="{GITHUB}">GitHub <span aria-hidden="true">↗</span></a><button class="search-trigger" data-search-open aria-label="{t['search_label']}" hidden><span>{t['search']}</span><kbd>/</kbd></button></div>
</div></header>'''


def footer(lang, current):
    t = TEXT[lang]
    return f'''<footer class="site-footer"><div class="footer-main"><a class="brand" href="{relative(current,page_path(lang))}" aria-label="{t['back_home']}"><img class="brand-logo" src="{relative(current,'assets/miblo-logo.svg')}" width="350" height="102" alt=""></a><div class="footer-links"><a href="{relative(current,page_path(lang,'index'))}">Documentation</a><a href="{GITHUB}">GitHub ↗</a><a href="{CRATES}">crates.io ↗</a><a href="{RELEASE}">{"Téléchargements" if lang == "fr" else "Downloads"} ↗</a><a href="https://github.com/NaSuRall/miblo_templates/releases">Templates ↗</a></div></div><div class="footer-bottom"><span>Open source · MIT · {t['credit']}</span><span>Rust / Axum / SQLx</span></div></footer>'''


def search_dialog(lang):
    t = TEXT[lang]
    return f'''<dialog class="search-dialog" aria-labelledby="search-title"><div class="search-head"><label id="search-title" for="search-input"><span class="blue">/</span> {t['search_title']}</label><button class="text-button" data-search-close aria-label="{t['close_search']}">{t['esc']} ×</button></div><input id="search-input" type="search" placeholder="{t['placeholder']}" autocomplete="off" spellcheck="false" aria-controls="search-results"><p id="search-status" class="search-status" role="status">{t['search_help']}</p><div id="search-results" class="search-results"></div><div class="search-help">{t['browse_keys']} <span>{t['enter']}</span></div></dialog><div class="toast" role="status" aria-live="polite"></div>'''


def structured_data(lang, path, key, title, description):
    url = canonical(path)
    website = {'@type':'WebSite','@id':BASE+'/#website','url':BASE+'/','name':'Miblo','inLanguage':['en','fr']}
    software = {'@type':'SoftwareApplication','@id':BASE+'/#software','name':'Miblo','url':BASE+'/','applicationCategory':'DeveloperApplication','operatingSystem':'Windows, macOS, Linux','softwareVersion':VERSION,'inLanguage':['en','fr'],'downloadUrl':RELEASE,'releaseNotes':RELEASE,'description':TEXT[lang]['home_description'],'isAccessibleForFree':True,'license':'https://opensource.org/license/mit','sameAs':GITHUB,'softwareHelp':canonical(page_path(lang,'index')),'softwareRequirements':'Rust 1.88+, Cargo, rustfmt and native build tools','author':{'@type':'Person','name':'NaSuRall','url':'https://github.com/NaSuRall'}}
    page = {'@type':'WebPage' if key is None else 'TechArticle','@id':url+'#page','url':url,'name':title,'headline':title,'description':description,'inLanguage':lang,'isPartOf':{'@id':BASE+'/#website'},'about':{'@id':BASE+'/#software'}}
    graph = [website, software, page]
    if key is not None:
        items = [('Miblo',canonical(page_path(lang))),('Documentation',canonical(page_path(lang,'index')))]
        if key != 'index': items.append((title,url))
        graph.append({'@type':'BreadcrumbList','@id':url+'#breadcrumbs','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':link} for i,(name,link) in enumerate(items)]})
        page['breadcrumb'] = {'@id':url+'#breadcrumbs'}
    return json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')


def page(lang, title, description, body, path, key=None):
    t = TEXT[lang]
    url = canonical(path)
    verification = f'<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">' if lang == 'en' and key is None else ''
    alt = ''.join(f'<link rel="alternate" hreflang="{other}" href="{canonical(page_path(other,key))}">' for other in ('en','fr'))
    alt += f'<link rel="alternate" hreflang="x-default" href="{canonical(page_path("en",key))}">'
    locale = 'en_US' if lang == 'en' else 'fr_FR'
    other_locale = 'fr_FR' if lang == 'en' else 'en_US'
    social = BASE + f'/assets/social-{lang}.png'
    extra = f'<link rel="stylesheet" href="{asset(path,"docs.css")}">' if key is not None else f'<link rel="stylesheet" href="{asset(path,"demo.css")}"><link rel="stylesheet" href="{asset(path,"assets/miblo-demo.css")}"><script defer src="{asset(path,"demo.js")}"></script>'
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">{verification}<meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{html.escape(description,quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#0c0e12"><meta name="color-scheme" content="dark"><link rel="canonical" href="{url}">{alt}<meta property="og:type" content="{'article' if key is not None else 'website'}"><meta property="og:site_name" content="Miblo"><meta property="og:locale" content="{locale}"><meta property="og:locale:alternate" content="{other_locale}"><meta property="og:title" content="{html.escape(title,quote=True)}"><meta property="og:description" content="{html.escape(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{social}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{t['image_alt']}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(title,quote=True)}"><meta name="twitter:description" content="{html.escape(description,quote=True)}"><meta name="twitter:image" content="{social}"><meta name="twitter:image:alt" content="{t['image_alt']}"><link rel="icon" href="{asset(path,'favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{asset(path,'style.css')}"><script defer src="{asset(path,'app.js')}"></script>{extra}<script type="application/ld+json">{structured_data(lang,path,key,title,description)}</script></head><body class="{'docs-page' if key is not None else 'home-page'}" data-search-index="{relative(path,'search-index.json' if lang == 'en' else 'fr/search-index.json')}" data-docs-home="{relative(path,page_path(lang,'index'))}">{header(lang,path,key)}{body}{footer(lang,path)}{search_dialog(lang)}</body></html>'''


def sidebar(lang, current):
    t = TEXT[lang]
    out = [f'<aside class="docs-sidebar"><details class="docs-menu" open><summary>{t["menu"]} <span>+</span></summary><nav aria-label="{t["chapters"]}">']
    group = None
    for item in PAGES[lang]:
        if item['group'] != group:
            if group is not None: out.append('</ul>')
            group = item['group']
            out.append(f'<p class="nav-group">{html.escape(group)}</p><ul>')
        active = ' aria-current="page"' if item['slug'] == current else ''
        out.append(f'<li><a href="{relative(page_path(lang,current),page_path(lang,item["slug"]))}"{active}><span aria-hidden="true">{">" if active else "·"}</span> {html.escape(item["title"])}</a></li>')
    out.append(f'</ul></nav><a class="sidebar-source" href="{GITHUB}">{t["source"]} ↗</a></details></aside>')
    return ''.join(out)


def plain(value):
    value = re.sub(r'<div class="code-header">.*?</div>', '', value, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value))).strip()


def recording_poster():
    recording = json.loads((ROOT / 'assets/miblo-demo.json').read_text())
    ansi = dict(black='#000000',red='#cd0000',green='#00cd00',brown='#cdcd00',blue='#0000ee',magenta='#cd00cd',cyan='#00cdcd',white='#e5e5e5')
    def color(value, default):
        if value == 'default': return default
        return '#' + value if re.fullmatch('[0-9a-f]{6}',value) else ansi[value]
    rules = ['/* Generated from the real terminal recording. */']
    for i,(fg,bg,bold,italic,underline,reverse) in enumerate(recording['styles']):
        fg,bg = color(fg,'#e0e6f5'),color(bg,'#0f121d')
        if reverse: fg,bg = bg,fg
        rules.append(f'.terminal-style-{i} {{ color: {fg}; background: {bg}; font-weight: {700 if bold else 400}; font-style: {"italic" if italic else "normal"}; text-decoration: {"underline" if underline else "none"}; }}')
    (ROOT/'assets/miblo-demo.css').write_text('\n'.join(rules)+'\n')
    return ''.join('<span class="terminal-row">'+''.join(f'<span class="terminal-style-{style}">{html.escape(text)}</span>' for style,text in row)+'</span>' for row in recording['frames'][0]['rows'])


def write(path, value):
    file = ROOT / path
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(value,encoding='utf-8')


def main():
    poster = recording_poster()
    paths = []
    for lang, pages in PAGES.items():
        t = TEXT[lang]
        home_path = page_path(lang)
        home = (ROOT / ('content/home_en.html' if lang == 'en' else 'content/home.html')).read_text().replace('<!-- DEMO_POSTER -->',poster).replace('{{VERSION}}', VERSION).replace('{{RELEASE}}', RELEASE).replace('{{DEMO_VERSION}}', json.loads((ROOT/'assets/miblo-demo.json').read_text())['cliVersion']).replace('{{RECORDING}}', asset(home_path,'assets/miblo-demo.json')).replace('{{DEMO_LABELS}}', asset(home_path,'assets/demo-en.json'))
        write(home_path,page(lang,t['home_title'],t['home_description'],localized_links(home,lang,home_path,True),home_path))
        paths.append(home_path)
        search = []
        for i,item in enumerate(pages):
            key = item['slug']
            path = page_path(lang,key)
            toc = ''.join(f'<li><a href="#{s["id"]}">{html.escape(s["title"])}</a></li>' for s in item['sections'])
            sections = ''.join(f'<section class="doc-section" id="{s["id"]}"><h2>{html.escape(s["title"])}</h2>{localized_links(s["body"],lang,path)}</section>' for s in item['sections'])
            prev = f'<a href="{relative(path,page_path(lang,pages[i-1]["slug"]))}"><span>{t["previous"]}</span>{pages[i-1]["title"]}</a>' if i else '<span></span>'
            nxt = f'<a href="{relative(path,page_path(lang,pages[i+1]["slug"]))}"><span>{t["next"]}</span>{pages[i+1]["title"]}</a>' if i+1<len(pages) else f'<a href="{relative(path,home_path)}"><span>{t["back"]}</span>{t["view_demo"]}</a>'
            demo = f'<a class="doc-demo-link" href="{relative(path,home_path)}?demo={DEMO_GUIDES[key]}#demo">▶ {t["view_demo"]} <span aria-hidden="true">→</span></a>' if key in DEMO_GUIDES else ''
            breadcrumb = SLUGS[key] if lang == 'en' else key
            body = f'''<div class="docs-layout">{sidebar(lang,key)}<main class="doc-content" id="contenu"><div class="breadcrumb"><a href="{relative(path,home_path)}">~/miblo</a>/<a href="{relative(path,page_path(lang,'index'))}">docs</a>/<span>{breadcrumb}</span></div><div class="doc-heading"><h1>{html.escape(item['title'])}</h1><p class="lead">{html.escape(item['intro'])}</p>{demo}</div>{sections}<nav class="doc-pagination" aria-label="{t['pagination']}">{prev}{nxt}</nav><p class="doc-feedback"><a href="{GITHUB}/issues">{t['report']} ↗</a></p></main><aside class="docs-toc"><p>{t['on_page']}</p><nav aria-label="{t['toc']}"><ul>{toc}</ul></nav><div class="doc-version"><span class="status-dot"></span> Documentation {VERSION}<br><span>Templates 0.6.0</span></div></aside></div>'''
            write(path,page(lang,f'{item["title"]} — {"Miblo documentation" if lang == "en" else "Documentation Miblo"}',item['intro'],body,path,key))
            paths.append(path)
            search.append(dict(title=item['title'],section=t['overview'],url=path,text=item['intro'],overview=True))
            for section in item['sections']:
                search.append(dict(title=item['title'],section=section['title'],url=path+'#'+section['id'],text=plain(section['body'])))
        write('search-index.json' if lang=='en' else 'fr/search-index.json',json.dumps(search,ensure_ascii=False,separators=(',',':')))
    urls = ''.join(f'<url><loc>{canonical(path)}</loc></url>' for path in paths)
    write('sitemap.xml',f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    print(f'Built {len(paths)} pages in English and French, two search indexes and sitemap.')


if __name__ == '__main__':
    main()
