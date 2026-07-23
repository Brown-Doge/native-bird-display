#!/usr/bin/env python3
# One-time reprocess: fill the Acer VG240Y panel (1920x1080 native, mounted
# in portrait so the effective viewport is 1080x1920) completely -- no
# letterbox/pillarbox bars. Cover-fits each 900x1200 card (scale to fill,
# center-crop the overflow) rather than padding, since the card's own
# background padding is too tight (~24px) to reach 9:16 without cropping
# into real content either way; a centered crop loses a little off both
# ends of each line but keeps every panel and the photo intact edge-to-edge.
# Run once from the repo root: py tools/reframe_to_1080x1920.py
from PIL import Image
import glob, os

TARGET_W, TARGET_H = 1080, 1920

FRAMEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frames')
files = sorted(glob.glob(os.path.join(FRAMEDIR, '*.jpg')))
print(f'reframing {len(files)} frames -> {TARGET_W}x{TARGET_H} (cover-crop, no bars)')

for f in files:
    im = Image.open(f).convert('RGB')
    w, h = im.size
    scale = max(TARGET_W / w, TARGET_H / h)
    new_w, new_h = round(w * scale), round(h * scale)
    im = im.resize((new_w, new_h), Image.LANCZOS)

    x = (new_w - TARGET_W) // 2
    y = (new_h - TARGET_H) // 2
    im = im.crop((x, y, x + TARGET_W, y + TARGET_H))
    im.save(f, quality=92)

print('done')
