# 🐦 Native Bird Lobby Display

A lobby/kiosk slideshow of native bird species found at a Monterey County
golf course. Runs unattended on a Raspberry Pi Zero W, feeding a spare,
otherwise-unused monitor.

> **Status:** first iteration. Originally prototyped on a Raspberry Pi 4
> (browser-based); ported to Pi Zero W for cost and easier deployment.

---

## Content

- **39 native bird species** (Central Coast / Salinas Valley area)
- Descriptions, citations, and photos are all sourced from the
  **National Audubon Society**

### Why Audubon

Every slide is built as a self-contained, properly-credited card rather
than a bare photo, so the source is documented in the display itself:

- **Description & facts** (habitat, diet, length, range) come from
  Audubon's [Field Guide](https://www.audubon.org/field-guide) entry
  for that species — cited on the card as
  `National Audubon Society • audubon.org/field-guide/bird/<species>`
- **Photo credit** for each image is overlaid on the photo itself
  (photographer name / *Audubon Photography Awards*), since most
  photos are drawn from that program
- Common name + scientific (Latin) name are both shown, matching
  Audubon's own field guide format

This keeps every bird slide individually sourced and citable, with no
separate credits file to maintain or lose track of.

## Hardware & Deployment

| | |
|---|---|
| **Board** | Raspberry Pi Zero W — cheap, compact, easy to fit behind existing lobby monitors |
| **Tradeoff** | Very limited RAM compared to the Pi 4 |
| **Placement** | Lodged in the back of an unused monitor, directly behind the screen — no visible extra hardware |
| **Operation** | One power switch turns everything on. No setup step for staff or guests — boots straight into the slideshow automatically |

## Pi Zero constraints

Because the Zero W has much less RAM than the Pi 4, the plan for this
build is to trim things down:

- No extra animation effects (e.g. Ken Burns pan/zoom) — just a simple crossfade
- **2 photos per bird**, instead of 3

> ⚠️ **Not yet implemented.** The current code (`birdshow.py`,
> `PER_BIRD = 3`) and `frames/` folder (117 images = 39 birds × 3 photos)
> still reflect the original 3-photo layout. This trim is the
> next-iteration TODO, not the current state — don't assume it's done.

## Files

```
birdshow.py   # the program you run
frames/       # the slide images it shows
```

## Run it

One-time install, then run:

```bash
sudo apt install -y python3-pygame
python3 birdshow.py
```

## Controls

| Key | Action |
|---|---|
| `→` | Next bird |
| `←` | Previous bird |
| `Space` | Pause |
| `R` | Rotate screen 90° (remembered across restarts) |
| `Q` / `Esc` | Quit |
