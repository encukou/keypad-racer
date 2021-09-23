"""Font generator.
Needs pillow and msdf-atlas-gen.

After running this, recompress the resulting PNG for faster loading:
    pngcrush -f 0 fontprep/font.png game/font.png
"""

import subprocess
import string
import json
import struct
import zlib

from PIL import Image
from PIL.PngImagePlugin import PngInfo

CHARS = string.printable + '÷'

with open('charset.txt', 'w') as f:
    print(*(ord(c) for c in CHARS), file=f)

CHARS2 = '←↑→↓⇦×⇫∗☒⇥⇤⁇↲∧⊘☼⌥⇧≡▼▲⇐⇒↹₤↰↨⊘☒⌘◆‖⌃⌒'

with open('charset_sym.txt', 'w') as f:
    print(*(ord(c) for c in sorted(CHARS2)), file=f)

subprocess.run(
    [
        'msdf-atlas-gen/bin/msdf-atlas-gen',
        '-font', 'gemunu-libre/GemunuLibre-Medium.ttf',
            '-charset', 'charset.txt',
            '-fontname', 'regular',
        #'-and', '-font', 'Rubik/fonts/ttf/Rubik-MediumItalic.ttf',
        #    '-charset', 'charset.txt',
        #    '-fontname', 'italic',
        '-and', '-font', 'm-plus-font/MPLUS1p-Medium.ttf',
            '-charset', 'charset_sym.txt',
            '-fontname', 'fallback',
        '-type', 'mtsdf',
        '-json', 'atlas.json',
        '-format', 'png', '-imageout', 'atlas.png',
        '-size', '50',
        '-square',
        '-errorcorrection', 'auto-full',
        '-overlap',
        '-pxrange', '20',
    ],
    check=True,
)

with open('atlas.json') as f:
    data = json.load(f)

pnginfo = PngInfo()
chars_info = bytearray()

def get_bounds(bounds):
    if bounds is None:
        return 0, 0, 0, 0
    return [bounds.get(k) for k in ('left', 'bottom', 'right', 'top')]

for i, variant in enumerate(data['variants']):
    metrics = variant['metrics']
    pnginfo.add(
        b'faCe',
        struct.pack('<e', metrics['lineHeight'])
        + variant['name'].encode(),
    )
    scale = 1 / (metrics['ascender'] - metrics['descender'])
    for glyph in variant['glyphs']:
        chars_info.extend(struct.pack(
            '<BIe4e4e',
            i,
            glyph['unicode'],
            glyph['advance'],
            *get_bounds(glyph.get('planeBounds')),
            *get_bounds(glyph.get('atlasBounds')),
        ))
pnginfo.add(b'foNt', zlib.compress(chars_info, zlib.Z_BEST_COMPRESSION))

image = Image.open('atlas.png')
image.save('font.png', pnginfo=pnginfo)

