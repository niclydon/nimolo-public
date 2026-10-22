#!/usr/bin/env python3
"""Emit PNG frames for the MacBook pet overlay from the Pane
pet factory sources (RGB565 + 1-bit masks -> RGBA PNGs,
nearest-neighbour 2x for retina crispness)."""
import re
import sys
from pathlib import Path
from PIL import Image

PETS = ["lucas", "mike", "carbon"]
FRAMES = {"idle": "IDLE", "walk_r0": "WALK0", "walk_r1": "WALK1",
          "walk_r2": "WALK2", "walk_l0": "WALKL0", "walk_l1": "WALKL1",
          "walk_l2": "WALKL2", "walk_l3": "WALKL3", "peace": "PEACE",
          "sit": "SIT", "sleep": "SLEEP"}


def grab(text, name):
    m = re.search(re.escape(name) + r"\[\d+\] PROGMEM = \{([^}]+)\}", text)
    if not m:
        raise SystemExit(f"missing array {name}")
    return [v.strip() for v in m.group(1).split(",") if v.strip()]


def main():
    src_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    for slug in PETS:
        text = (src_dir / f"pet_{slug}.cpp").read_text()
        up = slug.upper()
        for out_name, frame in FRAMES.items():
            px = [int(v, 16) for v in grab(text, f"PET_{up}_{frame}")]
            mk = [int(v, 16) for v in grab(text, f"PET_{up}_{frame}_MASK")]
            assert len(px) == 14400 and len(mk) == 1800, (slug, frame)
            img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
            pix = img.load()
            for i, c in enumerate(px):
                on = (mk[i // 8] >> (7 - (i % 8))) & 1
                if not on:
                    continue
                r = ((c >> 11) & 0x1F) << 3
                g = ((c >> 5) & 0x3F) << 2
                b = (c & 0x1F) << 3
                pix[i % 120, i // 120] = (r, g, b, 255)
            img = img.resize((240, 240), Image.NEAREST)
            dest = out_dir / slug
            dest.mkdir(parents=True, exist_ok=True)
            img.save(dest / f"{out_name}.png")
        print("ok:", slug)


if __name__ == "__main__":
    main()
