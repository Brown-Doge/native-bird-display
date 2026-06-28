#!/usr/bin/env python3
# AllBirds slideshow for Raspberry Pi Zero W (ARMv6) — smooth-fade build.
# Keeps the cross-fades; renders them efficiently for the Zero's old chip.
# Controls: RIGHT=next bird  LEFT=prev bird  SPACE=pause  Q/ESC=quit
import pygame, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Find the frames folder wherever it lives, so this file runs from
# the repo root OR from inside the pizero folder without moving anything.
CANDIDATES = [
    os.path.join(HERE, 'frames'),
    os.path.join(HERE, 'pizero', 'frames'),
    os.path.join(HERE, '..', 'pizero', 'frames'),
    os.path.join(os.path.expanduser('~'),
                 'Documents', 'native-bird-display', 'pizero', 'frames'),
]
FRAMEDIR = next((d for d in CANDIDATES
                 if os.path.isdir(d) and glob.glob(os.path.join(d, '*.jpg'))), None)
if FRAMEDIR is None:
    print('Could not find the frames folder. Looked in:')
    for d in CANDIDATES: print('  ', os.path.abspath(d))
    sys.exit(1)
FRAMES = sorted(glob.glob(os.path.join(FRAMEDIR, '*.jpg')))
PHOTO_MS   = 7000          # hold time per photo
FADE_MS    = 900           # fade length (time-based, not step-based)
PER_BIRD   = 3
N = len(FRAMES)

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
W, H = screen.get_size()

# Pre-scale ONCE to the exact on-screen size, so fading never rescales.
def load(idx):
    img = pygame.image.load(FRAMES[idx]).convert()
    iw, ih = img.get_size()
    surf = pygame.transform.smoothscale(img, (int(iw * H / ih), H))
    return surf

XOFF_CACHE = {}
def xoff(surf):
    return (W - surf.get_width()) // 2

# Black backdrop drawn once; we only repaint the card area during fades.
def paint_static(surf):
    screen.fill((0, 0, 0))
    screen.blit(surf, (xoff(surf), 0))
    pygame.display.flip()

def crossfade(cur, nxt):
    """Time-based fade: smooth regardless of how slow the chip is.
    Only the card rectangle is touched, and per-pixel alpha is set once."""
    x = xoff(nxt)
    cx = xoff(cur)
    rect = pygame.Rect(min(x, cx), 0, max(cur.get_width(), nxt.get_width()), H)
    top = nxt.convert_alpha()
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    while True:
        t = (pygame.time.get_ticks() - start) / FADE_MS
        if t >= 1: break
        a = int(255 * t)
        screen.fill((0, 0, 0), rect)
        screen.blit(cur, (cx, 0))
        top.set_alpha(a)
        screen.blit(top, (x, 0))
        pygame.display.update(rect)     # update only the card area, not whole screen
        pygame.event.pump()
        clock.tick(60)
    paint_static(nxt)                   # land cleanly on the final image

i = 0
cur = load(i)
paint_static(cur)
nxt_i = (i + 1) % N
nxt = load(nxt_i)
last = pygame.time.get_ticks()
paused = False; running = True
clock = pygame.time.Clock()

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
            elif e.key in (pygame.K_RIGHT, pygame.K_LEFT):
                step = 1 if e.key == pygame.K_RIGHT else -1
                tgt = (((i // PER_BIRD) + step) % (N // PER_BIRD)) * PER_BIRD
                t = load(tgt); crossfade(cur, t); cur = t; i = tgt
                nxt_i = (i + 1) % N; nxt = load(nxt_i)
                last = pygame.time.get_ticks()
            elif e.key == pygame.K_SPACE:
                paused = not paused
    if not paused and pygame.time.get_ticks() - last >= PHOTO_MS:
        if nxt is None: nxt = load(nxt_i)
        crossfade(cur, nxt); cur = nxt; i = nxt_i
        nxt_i = (i + 1) % N
        nxt = load(nxt_i)
        last = pygame.time.get_ticks()
    clock.tick(30)
pygame.quit()
