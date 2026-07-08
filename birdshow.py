#!/usr/bin/env python3
# AllBirds slideshow for Raspberry Pi Zero W (ARMv6) — portrait build.
# Rotates output 90 deg so it reads upright on a physically-rotated (portrait) monitor.
# Frames are fit to the screen (no crop, no stretch); crossfades preserved.
# Controls: RIGHT=next bird  LEFT=prev bird  SPACE=pause  Q/ESC=quit
#
# If the picture comes out UPSIDE DOWN, change ROTATE = 90 to ROTATE = 270.
import pygame, os, glob, sys

ROTATE = 90                # 90 or 270, depending on which way you flip the monitor

HERE = os.path.dirname(os.path.abspath(__file__))
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
PHOTO_MS = 7000
FADE_MS  = 900
PER_BIRD = 3
N = len(FRAMES)

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
W, H = screen.get_size()

# Work out the fixed on-screen rectangle ALL frames land in.
# Rotate a sample, fit it to the screen with no stretch, and center it.
_s = pygame.image.load(FRAMES[0]).convert()
_s = pygame.transform.rotate(_s, ROTATE)
rw, rh = _s.get_size()
scale = min(W / rw, H / rh)
TW, TH = int(rw * scale), int(rh * scale)
BX, BY = (W - TW) // 2, (H - TH) // 2
IMG_RECT = pygame.Rect(BX, BY, TW, TH)

def load(idx):
    img = pygame.image.load(FRAMES[idx]).convert()
    img = pygame.transform.rotate(img, ROTATE)
    return pygame.transform.smoothscale(img, (TW, TH))

def paint_static(surf):
    screen.fill((0, 0, 0))
    screen.blit(surf, (BX, BY))
    pygame.display.flip()

def crossfade(cur, nxt):
    top = nxt.convert_alpha()
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    while True:
        t = (pygame.time.get_ticks() - start) / FADE_MS
        if t >= 1: break
        screen.fill((0, 0, 0), IMG_RECT)
        screen.blit(cur, (BX, BY))
        top.set_alpha(int(255 * t))
        screen.blit(top, (BX, BY))
        pygame.display.update(IMG_RECT)
        pygame.event.pump()
        clock.tick(60)
    paint_static(nxt)

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
