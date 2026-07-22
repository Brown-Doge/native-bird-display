#!/usr/bin/env python3
# One-time reprocess: fit each 900x1200 card to the Acer VG240Y panel
# (1920x1080 native, mounted in portrait so the effective viewport is
# 1080x1920). Scales to fill the full 1080 width, then pads top/bottom
# with the card's own solid background color -- no crop, no stretch,
# no visible seam. Run once from the repo root: py tools/reframe_to_1080x1920.py
from PIL import Image
import glob, os

TARGET_W, TARGET_H = 1080, 1920
BG = (15, 28, 10)  # solid background color shared by every card

FRAMEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frames')
files = sorted(glob.glob(os.path.join(FRAMEDIR, '*.jpg')))
print(f'reframing {len(files)} frames -> {TARGET_W}x{TARGET_H}')

for f in files:
    im = Image.open(f).convert('RGB')
    w, h = im.size
    scale = TARGET_W / w
    new_w, new_h = TARGET_W, round(h * scale)
    im = im.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new('RGB', (TARGET_W, TARGET_H), BG)
    y = (TARGET_H - new_h) // 2
    canvas.paste(im, (0, y))
    canvas.save(f, quality=92)

print('done')
