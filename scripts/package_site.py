#!/usr/bin/env python3
"""Package only public website files for the existing Hostinger document root."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
files = [ROOT/name for name in ('.htaccess','index.html','style.css','docs.css','demo.css','app.js','demo.js','analytics.js','favicon.svg','search-index.json','sitemap.xml','robots.txt','llms.txt')]
for directory in ('docs','en','fr','assets'):
    files.extend(file for file in (ROOT/directory).rglob('*') if file.is_file() and file.suffix in ('.html','.css','.js','.json','.svg','.png'))
files.extend(ROOT.glob('google*.html'))
assert all(file.is_file() and not file.is_symlink() for file in files)
args.output.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(args.output,'w',ZIP_DEFLATED) as archive:
    for file in sorted(set(files)): archive.write(file,file.relative_to(ROOT))
with ZipFile(args.output) as archive:
    assert archive.testzip() is None
    print(f'{args.output}: {len(archive.namelist())} public files, {args.output.stat().st_size} bytes')
