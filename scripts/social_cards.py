"""Deterministic editorial share graphics; no remote images or rendering service."""
from pathlib import Path
import hashlib
import json
import os
import struct

LAYOUT = 'darkecho-editorial-2'
WIDTH, HEIGHT = 1200, 630


def png_size(path):
    with Path(path).open('rb') as stream:
        header = stream.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not a PNG: ' + str(path))
    return struct.unpack('>II', header[16:24])


def font_path(arabic=False, bold=False):
    windows = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    # Mixed Arabic/Latin titles need a font covering both scripts.
    choices = [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), windows / ('arialbd.ttf' if bold else 'arial.ttf')]
    return next((str(p) for p in choices if p.is_file()), 'DejaVuSans.ttf')


def render_card(path, item):
    try:
        from PIL import Image, ImageDraw, ImageFont, features
    except ImportError as exc:
        raise RuntimeError('New sharing cards need Pillow: python -m pip install -r requirements-build.txt') from exc
    arabic = item.get('lang') == 'ar'
    if arabic and not features.check('raqm'):
        raise RuntimeError('Arabic sharing cards require a Pillow build with libraqm shaping support.')
    image = Image.new('RGB', (WIDTH, HEIGHT), '#0c0a10')
    draw = ImageDraw.Draw(image)
    accent = {'maze': '#d7ba76', 'house': '#9ec8be', 'signal': '#ed9caf', 'guide': '#aeb4ef', 'quiz': '#e4af86'}.get(item['theme'], '#ed9caf')
    draw.polygon([(740, 0), (1200, 0), (1200, 630), (490, 630)], fill='#18131f')
    for x in range(740, 1250, 55):
        draw.line([(x, 0), (x-220, 630)], fill='#2b2232', width=1)
    draw.rounded_rectangle((49, 41, 1151, 589), radius=18, outline='#493344', width=2)
    draw.polygon([(76, 70), (87, 70), (75, 112), (64, 112)], fill='#e64c70')
    brand = ImageFont.truetype(font_path(bold=True), 27)
    draw.text((101, 73), 'DARK ECHO', font=brand, fill='#f6edf3', stroke_width=0)
    small = ImageFont.truetype(font_path(), 22)
    draw.text((76, 531), 'TRACE THE SOURCE. KEEP THE MYSTERY.', font=small, fill='#b5a5b8')
    draw.text((76, 562), 'darkechoproject.github.io/darkecho', font=ImageFont.truetype(font_path(), 17), fill='#a493a8')
    draw.line((76, 138, 1124, 138), fill=accent, width=3)
    label_font = ImageFont.truetype(font_path(arabic, True), 25)
    options = {'direction': 'rtl', 'language': 'ar'} if arabic else {}
    anchor = 'ra' if arabic else 'la'
    x = 1110 if arabic else 76
    draw.text((x, 163), item['label'], font=label_font, anchor=anchor, fill=accent, **options)
    words = item['title'].split()
    for size in range(67 if arabic else 63, 35, -2):
        font = ImageFont.truetype(font_path(arabic, True), size)
        lines, current = [], ''
        for word in words:
            candidate = (current + ' ' + word).strip()
            if current and draw.textlength(candidate, font=font, **options) > 1010:
                lines.append(current); current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        step = int(size * (1.47 if arabic else 1.25))
        if len(lines) <= 3 and len(lines) * step <= 264:
            break
    if len(lines) > 3 or any(draw.textlength(line, font=font, **options) > 1010 for line in lines):
        raise ValueError('Share-card title does not fit: ' + item['title'])
    y = 221
    for line in lines:
        draw.text((x, y), line, font=font, anchor=anchor, fill='#fff1f7', **options)
        y += step
    if item['theme'] == 'maze':
        for i in range(3):
            draw.rectangle((1010+i*15, 458+i*10, 1110-i*15, 515-i*10), outline=accent, width=2)
    elif item['theme'] == 'house':
        draw.rectangle((1020, 459, 1110, 515), outline=accent, width=2)
        draw.line((1065, 459, 1065, 515), fill=accent, width=2)
        draw.line((1020, 487, 1110, 487), fill=accent, width=2)
    elif item['theme'] == 'signal':
        for i, height in enumerate([12, 30, 19, 51, 29, 40, 14, 34]):
            draw.line((1020+i*12, 515-height, 1020+i*12, 515), fill=accent, width=5)
    else:
        draw.line((1020, 472, 1110, 472), fill=accent, width=3)
        draw.line((1020, 489, 1090, 489), fill=accent, width=3)
        draw.line((1020, 506, 1070, 506), fill=accent, width=3)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format='PNG', optimize=True)


def build_cards(root, items):
    root = Path(root)
    record_path = root / 'data/social-cards.json'
    old = json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else {}
    records, paths = {}, {}
    for item in items:
        key = item['page']
        relative = 'assets/social/' + item['key'] + '.png'
        digest = hashlib.sha256(json.dumps({'layout': LAYOUT, **item}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        target = root / relative
        prior = old.get(key, {})
        same = prior.get('digest') == digest and target.is_file() and png_size(target) == (WIDTH, HEIGHT)
        if same:
            same = prior.get('sha256') == hashlib.sha256(target.read_bytes()).hexdigest()
        if not same:
            render_card(target, item)
        records[key] = {'path': relative, 'digest': digest, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'width': WIDTH, 'height': HEIGHT, 'lang': item.get('lang', 'en')}
        paths[key] = relative
    record_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return paths
