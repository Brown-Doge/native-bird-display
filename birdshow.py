#!/usr/bin/env python3
# AllBirds slideshow for Raspberry Pi Zero W — low-memory version.
# Loads one image at a time so it fits in the Zero W's RAM.
# Controls: RIGHT=next bird  LEFT=prev bird  SPACE=pause  Q/ESC=quit
import pygame, os, glob, sys

HERE   = os.path.dirname(os.path.abspath(__file__))
FRAMES = sorted(glob.glob(os.path.join(HERE, 'frames', '*.jpg')))
PHOTO_MS   = 7000
FADE_STEPS = 10
PER_BIRD   = 3
N = len(FRAMES)
if N == 0:
    print('No frames found'); sys.exit(1)

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
W, H = screen.get_size()

def load(idx):
    img = pygame.image.load(FRAMES[idx]).convert()
    iw, ih = img.get_size()
    return pygame.transform.smoothscale(img, (int(iw * H / ih), H))

def show(surf):
    screen.fill((0, 0, 0))
    screen.blit(surf, ((W - surf.get_width()) // 2, 0))
    pygame.display.flip()

def crossfade(cur, nxt):
    x = (W - nxt.get_width()) // 2
    cx = (W - cur.get_width()) // 2
    t = nxt.copy()
    for s in range(1, FADE_STEPS + 1):
        screen.fill((0, 0, 0))
        screen.blit(cur, (cx, 0))
        t.set_alpha(int(255 * s / FADE_STEPS))
        screen.blit(t, (x, 0))
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(20)

i = 0
cur = load(i); show(cur)
nxt_i = (i + 1) % N
nxt = load(nxt_i)              # preload next while this one shows
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
        nxt = load(nxt_i)         # preload the following frame during the hold
        last = pygame.time.get_ticks()
    clock.tick(20)
pygame.quit()
