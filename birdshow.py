#!/usr/bin/env python3
# AllBirds slideshow for Raspberry Pi Zero W (ARMv6) — adaptive build.
# Auto-fits every frame to whatever screen it's on (any size, any orientation):
# no crop, no stretch; crossfades preserved.
#
# Rotation is adaptive:
#   * Default: frames are shown UPRIGHT and fit to the detected screen.
#   * If the picture comes out sideways or upside-down (e.g. a monitor that's
#     physically turned), press  R  to rotate it 90 deg at a time until it
#     looks right. Your choice is remembered across restarts
#     (saved to ~/.allbirds_rotation), so you only set it once per screen.
#   * Or force it at launch:  python3 birdshow.py --rotate 90   (0/90/180/270)
#
# Controls: RIGHT=next bird  LEFT=prev bird  SPACE=pause  R=rotate  Q/ESC=quit
import pygame, os, glob, sys

# ---------- locate frames (portable after a fresh clone) ----------
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

# ---------- rotation: --rotate arg  >  saved file  >  0 (upright) ----------
CFG = os.path.join(os.path.expanduser('~'), '.allbirds_rotation')

def read_saved_rotation():
    try:
        v = int(open(CFG).read().strip())
        return v if v in (0, 90, 180, 270) else None
    except Exception:
        return None

def save_rotation(v):
    try:
        open(CFG, 'w').write(str(v))
    except Exception:
        pass

ROTATE = None
argv = sys.argv[1:]
for j, a in enumerate(argv):
    if a == '--rotate' and j + 1 < len(argv):
        try: ROTATE = int(argv[j + 1])
        except ValueError: pass
    elif a.startswith('--rotate='):
        try: ROTATE = int(a.split('=', 1)[1])
        except ValueError: pass
if ROTATE not in (0, 90, 180, 270):
    ROTATE = None
if ROTATE is None:
    ROTATE = read_saved_rotation()
if ROTATE is None:
    ROTATE = 0                      # auto default: upright, fit to screen

# ---------- init ----------
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
W, H = screen.get_size()

# Placeholders; compute_layout() fills these based on the current ROTATE.
TW = TH = BX = BY = 0
IMG_RECT = pygame.Rect(0, 0, 0, 0)

def compute_layout():
    """Fit a (rotated) frame to the screen with no stretch/crop, centered."""
    global TW, TH, BX, BY, IMG_RECT
    s = pygame.image.load(FRAMES[0]).convert()
    if ROTATE:
        s = pygame.transform.rotate(s, ROTATE)
    rw, rh = s.get_size()
    scale = min(W / rw, H / rh)
    TW, TH = int(rw * scale), int(rh * scale)
    BX, BY = (W - TW) // 2, (H - TH) // 2
    IMG_RECT = pygame.Rect(BX, BY, TW, TH)

def load(idx):
    img = pygame.image.load(FRAMES[idx]).convert()
    if ROTATE:
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

compute_layout()
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
            elif e.key == pygame.K_r:
                # rotate the whole display 90 deg and remember it
                ROTATE = (ROTATE + 90) % 360
                save_rotation(ROTATE)
                compute_layout()
                cur = load(i)
                nxt = load(nxt_i)
                paint_static(cur)
                last = pygame.time.get_ticks()
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
