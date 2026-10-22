#!/usr/bin/env python3
"""Slice the per-pet expression sheets into Pip face frames.

Input : faces/source/<pet>-sheet.png  (4x2 grid, order below)
Output: faces/pip/<pet>/<expression>.bin   2048 bytes, 128x128,
        Adafruit GFX layout (row-major, MSB first) for pip_image
        faces/pip/<pet>/<expression>.png   the same frame as an image
        faces/previews/<pet>-faces-pip.png contact sheet (4x zoom)

The sheets are flat colour with near-black ink on white. A colour
threshold would turn hair and fur into solid blobs on a 1-bit
display, so the frames are LINE ART: a pixel lights when it is
much darker (ink strokes) or much brighter (whiskers on fur)
than its local neighbourhood. Fills vanish; every drawn stroke
survives, which is what reads at 128x128 on the SH1107.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).parent
EXPRESSIONS = ["content", "happy", "love", "sleepy",
               "surprised", "dizzy", "sad", "blink"]  # grid order
PETS = ["lucas", "mike", "carbon", "nova", "aria"]
SIZE = 128
FACE = 120          # target face height in the frame, px
INK_LUM = 48        # only true near-black strokes are ink outright
                    # (hair and beard fills sit at 60-130 and must
                    # stay dark, or Mike becomes one lit mass)
EDGE_DELTA = 70     # strong local drop onto a darkish pixel:
                    # an outline core, not a fill boundary
GREY_DELTA = 40     # mid-grey stroke on paper (outer whiskers)
LIGHT_DELTA = 45    # light stroke on a darker fill (whiskers)


def cell_bbox(cell: Image.Image) -> tuple[int, int, int, int]:
    """Bounding box of non-white content, searching the central
    region so a neighbour's whiskers cannot stretch the box."""
    g = np.asarray(cell.convert("L"), dtype=np.int16)
    mask = g < 242
    h, w = mask.shape
    cx0, cx1 = int(w * 0.02), int(w * 0.98)
    core = mask[:, cx0:cx1]
    ys, xs = np.nonzero(core)
    if len(ys) == 0:
        return (0, 0, w, h)
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min() + cx0, xs.max() + cx0
    # vertical extent from the full width (ears / hair tips)
    colmask = mask[y0:y1 + 1, :]
    xs2 = np.nonzero(colmask.any(axis=0))[0]
    x0, x1 = min(x0, xs2.min()), max(x1, xs2.max())
    pad = 16
    return (max(0, x0 - pad), max(0, y0 - pad),
            min(w, x1 + pad), min(h, y1 + pad))


def line_art(cell: Image.Image) -> Image.Image:
    box = cell_bbox(cell)
    crop = cell.crop(box).convert("L")
    scale = FACE / crop.height
    crop = crop.resize((round(crop.width * scale), FACE),
                       Image.LANCZOS)
    canvas = Image.new("L", (SIZE, SIZE), 255)
    canvas.paste(crop, ((SIZE - crop.width) // 2, (SIZE - FACE) // 2))
    g = np.asarray(canvas, dtype=np.int16)
    blur = np.asarray(canvas.filter(ImageFilter.GaussianBlur(5)),
                      dtype=np.int16)
    ink = (g < INK_LUM) \
        | ((blur - g > EDGE_DELTA) & (g < 120)) \
        | ((blur - g > GREY_DELTA) & (g >= 120) & (g < 238)) \
        | ((g - blur > LIGHT_DELTA) & (g > 150))
    # drop isolated specks
    up = np.zeros_like(ink); up[1:, :] = ink[:-1, :]
    dn = np.zeros_like(ink); dn[:-1, :] = ink[1:, :]
    lf = np.zeros_like(ink); lf[:, 1:] = ink[:, :-1]
    rt = np.zeros_like(ink); rt[:, :-1] = ink[:, 1:]
    ink &= (up | dn | lf | rt)
    out = np.where(ink, 255, 0).astype(np.uint8)
    return Image.fromarray(out, "L")


def pack_bits(img: Image.Image) -> bytes:
    a = np.asarray(img) > 0
    return np.packbits(a, axis=1).tobytes()


def main() -> int:
    index = {}
    for pet in PETS:
        sheet = Image.open(ROOT / "source" / f"{pet}-sheet.png")
        W, H = sheet.size
        cw, ch = W // 4, H // 2
        outdir = ROOT / "pip" / pet
        outdir.mkdir(parents=True, exist_ok=True)
        frames = []
        for i, expr in enumerate(EXPRESSIONS):
            cell = sheet.crop(((i % 4) * cw, (i // 4) * ch,
                               (i % 4 + 1) * cw, (i // 4 + 1) * ch))
            frame = line_art(cell)
            (outdir / f"{expr}.bin").write_bytes(pack_bits(frame))
            frame.save(outdir / f"{expr}.png")
            frames.append((expr, frame))
            index[f"{pet}/{expr}"] = f"pip/{pet}/{expr}.bin"
        prev = Image.new("L", (4 * SIZE * 3, 2 * (SIZE * 3 + 22)), 0)
        d = ImageDraw.Draw(prev)
        for i, (expr, frame) in enumerate(frames):
            big = frame.resize((SIZE * 3, SIZE * 3), Image.NEAREST)
            x, y = (i % 4) * SIZE * 3, (i // 4) * (SIZE * 3 + 22)
            prev.paste(big, (x, y))
            d.text((x + 8, y + SIZE * 3 + 4), expr, fill=255)
        pdir = ROOT / "previews"
        pdir.mkdir(exist_ok=True)
        prev.save(pdir / f"{pet}-faces-pip.png")
        print(pet, "ok")
    (ROOT / "pip" / "index.json").write_text(
        json.dumps(index, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
