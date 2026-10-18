#!/usr/bin/env python3
"""Slice a generated walk strip/grid into 8 registered 240x240 frames.

v3 (fixes the v2.5 judder for real): after v2's uniform scale and
ground-line placement, each frame is REGISTERED against frame 0:
an integer shift search minimises the alpha difference over the
upper 65% of the figure (head and torso), so the body stays pinned
and only the legs swing. Per-frame recentring let the body seesaw
by up to ~14px between poses, which read as skipping and blinking.
"""
import sys
from PIL import Image
import numpy as np

def figures(img):
    a = np.asarray(img.convert("RGB")).astype(int)
    fg = (a.sum(axis=2) < 720)
    rows = fg.any(axis=1)
    bands = []
    y = 0
    while y < len(rows):
        if rows[y]:
            y0 = y
            while y < len(rows) and (rows[y] or (y + 1 < len(rows) and rows[y + 1])):
                y += 1
            bands.append((y0, y))
        y += 1
    out = []
    for (y0, y1) in bands:
        sub = fg[y0:y1]
        cols = sub.any(axis=0)
        x = 0
        while x < len(cols):
            if cols[x]:
                x0 = x
                gap = 0
                while x < len(cols) and (cols[x] or gap < 12):
                    gap = 0 if cols[x] else gap + 1
                    x += 1
                out.append((x0, y0, x - gap, y1))
            x += 1
    return out

def key_white(crop):
    a = np.asarray(crop.convert("RGB")).astype(np.int16)
    d = 255 - a.min(axis=2)
    alpha = np.clip(d * 6, 0, 255)
    alpha = np.where(alpha < 40, 0, np.where(alpha > 215, 255, alpha)).astype(np.uint8)
    rgba = np.dstack([np.asarray(crop.convert("RGB")), alpha])
    return Image.fromarray(rgba, "RGBA")

def register(ref_alpha, img_alpha, max_dx, max_dy):
    """Shift (dx, dy) minimising alpha diff in the upper 65%."""
    H, W = ref_alpha.shape
    region = slice(0, int(H * 0.65))
    ref = ref_alpha[region].astype(np.int32)
    best, best_score = (0, 0), None
    for dy in range(-max_dy, max_dy + 1):
        for dx in range(-max_dx, max_dx + 1):
            shifted = np.roll(np.roll(img_alpha, dy, axis=0), dx, axis=1)
            score = np.abs(shifted[region].astype(np.int32) - ref).sum()
            if best_score is None or score < best_score:
                best, best_score = (dx, dy), score
    return best

def main(strip_path, pet):
    img = Image.open(strip_path).convert("RGB")
    boxes = figures(img)
    boxes.sort(key=lambda b: (round(b[1] / 100), b[0]))
    print(pet, "figures:", len(boxes))
    assert len(boxes) == 8, f"expected 8 figures, got {len(boxes)}"
    import os
    fdir = f"/home/hatch/workspace/pets/mac/frames/{pet}"
    heights, bottoms = [], []
    for n in ("idle",):
        im = Image.open(f"{fdir}/{n}.png").convert("RGBA")
        bb = im.getbbox()
        heights.append(bb[3] - bb[1]); bottoms.append(bb[3])
    target_h = float(np.median(heights)); base = int(np.median(bottoms))
    figs = []
    for (x0, y0, x1, y1) in boxes:
        crop = key_white(img.crop((x0, y0, x1, y1)))
        crop = crop.crop(crop.getbbox())
        figs.append(crop)
    med_h = float(np.median([f.height for f in figs]))
    scale = target_h / med_h
    canvases = []
    for crop in figs:
        crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
        canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
        canvas.alpha_composite(crop, ((240 - crop.width) // 2, base - crop.height))
        canvases.append(canvas)
    ref = np.asarray(canvases[0])[:, :, 3]
    max_dx = 4 if pet == "carbon" else 24
    shifts = []
    for i, canvas in enumerate(canvases):
        a = np.asarray(canvas)[:, :, 3]
        dx, dy = (0, 0) if i == 0 else register(ref, a, max_dx, 8)
        shifts.append((dx, dy))
        out = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
        out.alpha_composite(canvas, (dx, dy))
        out.save(f"{fdir}/walk_r{i}.png")
        out.transpose(Image.FLIP_LEFT_RIGHT).save(f"{fdir}/walk_l{i}.png")
    print(pet, "scale", round(scale, 3), "shifts", shifts)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
