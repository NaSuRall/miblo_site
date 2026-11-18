#!/usr/bin/env python3
"""Render tracked social cards. Optional authoring dependency: Pillow."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ['/System/Library/Fonts/Menlo.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']
font_path = next((path for path in FONTS if Path(path).is_file()), None)
if font_path is None: raise SystemExit('Install a monospace font or add its path to FONTS.')
logo = ET.parse(ROOT / 'assets/miblo-logo.svg').getroot()
for lang, heading, detail in [('en','Build your Rust API.','Models, routes and SQL migrations.'),('fr','Votre API prend forme.','Modèles, routes et migrations SQL.')]:
    image = Image.new('RGB',(1200,630),'#0c0e12')
    draw = ImageDraw.Draw(image)
    draw.rectangle((32,32,1167,597),outline='#303640',width=2)
    for rect in logo.iter('{http://www.w3.org/2000/svg}rect'):
        x,y,w,h = (float(rect.get(key,'0')) for key in ('x','y','width','height'))
        draw.rectangle((250+x*2,105+y*2,250+(x+w)*2-1,105+(y+h)*2-1),fill='#4696ff')
    for text,y,size,color in [(heading,355,36,'#e0e6f5'),(detail,417,24,'#9ca9bd'),('Axum / SQLx / SQLite / MySQL',468,22,'#9ca9bd'),('cli.miblo.fr',551,18,'#4696ff')]:
        draw.text((600,y),text,font=ImageFont.truetype(font_path,size),fill=color,anchor='mm')
    image.save(ROOT / f'assets/social-{lang}.png',optimize=True)
