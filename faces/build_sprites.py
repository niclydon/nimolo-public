#!/usr/bin/env python3
"""Slice pose sheets into 240x240 Mac/HQ sprite frames.

Input : faces/source/<pet>-poses.png  (4x2 grid)
        row 1: idle, peace, sit, sleep
        row 2: walk-left A, walk-left B, walk-right A, walk-right B
Output: mac/frames/<pet>/{idle,peace,sit,sleep}.png and
        walk_{l,r}0..7.png (the two strides alternated with a
        stride bob, the v1 walk set for sheet-generated members)

White background is flood-filled to transparency from the cell
borders; the character is scaled to FRAME_H px tall on a common
ground line, matching the factory frame geometry.
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).parent.parent          # pets repo root
SIZE = 240
FRAME_H = 218                                  # sprite height, px
GROUND = 236                                   # baseline y
PETS = sys.argv[1:] or ["nova", "aria"]
BOB = [0, -4, -7, -4, 0, -4, -7, -4]


def cutout(cell: Image.Image) -> Image.Image:
    """Flood-fill near-white from the borders to alpha 0."""
    rgb = cell.convert("RGB")
    a = np.asarray(rgb).astype(np.int16)
    near_white = (a.min(axis=2) > 204)
    h, w = near_white.shape
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        q.append((0, x)); q.append((h - 1, x))
    for y in range(h):
        q.append((y, 0)); q.append((y, w - 1))
    while q:
        y, x = q.popleft()
        if seen[y, x] or not near_white[y, x]:
            continue
        seen[y, x] = True
        if y: q.append((y - 1, x))
        if y < h - 1: q.append((y + 1, x))
        if x: q.append((y, x - 1))
        if x < w - 1: q.append((y, x + 1))
    out = rgb.convert("RGBA")
    alpha = np.where(seen, 0, 255).astype(np.uint8)
    # drop stray specks: art that bled in from a neighbouring cell
    # is a small disconnected component; keep the real character
    solid = alpha > 0
    lab = np.zeros(solid.shape, np.int32)
    cur, sizes = 0, {}
    hh, ww = solid.shape
    for sy in range(hh):
        for sx in range(ww):
            if not solid[sy, sx] or lab[sy, sx]:
                continue
            cur += 1
            n, q = 0, deque([(sy, sx)])
            lab[sy, sx] = cur
            while q:
                y, x = q.popleft(); n += 1
                for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                    if 0 <= ny < hh and 0 <= nx < ww \
                            and solid[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = cur; q.append((ny, nx))
            sizes[cur] = n
    if sizes:
        biggest = max(sizes.values())
        keep = {k for k, v in sizes.items() if v > 0.02 * biggest}
        alpha = np.where(np.isin(lab, list(keep)), alpha, 0)
    arr = np.asarray(out).copy()
    arr[:, :, 3] = alpha
    return Image.fromarray(arr, "RGBA")


def clean_frame(img: Image.Image) -> Image.Image:
    """Drop small disconnected alpha specks from a finished
    frame (sheet neighbours bleed in at the cell edges)."""
    a = np.asarray(img).copy()
    solid = a[:, :, 3] > 10
    h, w = solid.shape
    lab = np.zeros((h, w), np.int32)
    cur, sizes = 0, {}
    for sy in range(h):
        for sx in range(w):
            if not solid[sy, sx] or lab[sy, sx]:
                continue
            cur += 1
            n, q = 0, deque([(sy, sx)])
            lab[sy, sx] = cur
            while q:
                y, x = q.popleft(); n += 1
                for ny, nx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                    if 0 <= ny < h and 0 <= nx < w \
                            and solid[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = cur; q.append((ny, nx))
            sizes[cur] = n
    if sizes:
        biggest = max(sizes.values())
        keep = {k for k, v in sizes.items() if v > 0.03 * biggest}
        a[:, :, 3] = np.where(np.isin(lab, list(keep)),
                              a[:, :, 3], 0)
    return Image.fromarray(a, "RGBA")


def frame(cell: Image.Image, bob: int = 0) -> Image.Image:
    img = cutout(cell)
    box = img.getbbox()
    img = img.crop(box)
    scale = min(FRAME_H / img.height, (SIZE - 8) / img.width)
    img = img.resize((round(img.width * scale),
                      round(img.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(img, ((SIZE - img.width) // 2,
                       GROUND - img.height + bob), img)
    return clean_frame(canvas)


def main() -> int:
    for pet in PETS:
        sheet = Image.open(ROOT / "faces" / "source" / f"{pet}-poses.png")
        W, H = sheet.size
        cw, ch = W // 4, H // 2
        cells = [sheet.crop(((i % 4) * cw, (i // 4) * ch,
                             (i % 4 + 1) * cw, (i // 4 + 1) * ch))
                 for i in range(8)]
        out = ROOT / "mac" / "frames" / pet
        out.mkdir(parents=True, exist_ok=True)
        for name, cell in zip(["idle", "peace", "sit", "sleep"],
                              cells[:4]):
            frame(cell).save(out / f"{name}.png")
        for side, a, b in (("l", cells[4], cells[5]),
                           ("r", cells[6], cells[7])):
            fa, fb = frame(a), frame(b)
            for i in range(8):
                src = fa if i % 2 == 0 else fb
                canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
                canvas.paste(src, (0, BOB[i]), src)
                canvas.save(out / f"walk_{side}{i}.png")
        print(pet, "ok", len(list(out.glob('*.png'))), "frames")
    return 0


if __name__ == "__main__":
    sys.exit(main())
