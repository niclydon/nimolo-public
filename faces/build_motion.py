#!/usr/bin/env python3
"""Convert Kling face loops (faces/motion/*.mp4) into 1-bit
frame sequences for Pip-class faces: faces/pip-anim/<pet>/
<expr>/fNN.png plus fNN.bin device twins (2048 bytes each,
the pip_image layout), at 6 fps over the 5-second loops.

Polarity matches the face pack: bright art on black. The
colour masters are dark line art and colour fills on light
ground, so frames are inverted and thresholded; the result
reads as a filled silhouette, not the pack's line art. That
is deliberate: it is the faithful conversion of the loops.

Usage: python3 build_motion.py
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 6
THRESH = 110
LOOPS = {
    ("lucas", "content"):
        "motion/pets-lucas-loop.mp4",
    ("mike", "content"):
        "motion/pets-mike-loop.mp4",
    ("carbon", "content"):
        "motion/pets-carbon-idle-v2.mp4",
    ("carbon", "love"):
        "motion/pets-carbon-love-loop.mp4",
    ("nova", "content"):
        "motion/pets-nova-loop.mp4",
    ("aria", "content"):
        "motion/pets-aria-loop.mp4",
}


def convert(src: str, outdir: str) -> int:
    os.makedirs(outdir, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", src, "-vf",
             f"fps={FPS},scale=128:128",
             os.path.join(td, "f%03d.png")], check=True)
        n = 0
        for name in sorted(os.listdir(td)):
            im = Image.open(os.path.join(td, name)).convert("L")
            im = im.point(lambda v: 255 if (255 - v) > THRESH else 0)
            stem = "f%02d" % (int(name[1:4]) - 1)
            im.save(os.path.join(outdir, stem + ".png"))
            bits = im.convert("1")
            data = bits.tobytes()
            assert len(data) == 2048, len(data)
            with open(os.path.join(outdir, stem + ".bin"), "wb") as fh:
                fh.write(data)
            n += 1
    return n


def main() -> int:
    index = {}
    for (pet, expr), rel in LOOPS.items():
        out = os.path.join(HERE, "pip-anim", pet, expr)
        n = convert(os.path.join(HERE, rel), out)
        index[f"{pet}/{expr}"] = {"frames": n, "fps": FPS}
        print(f"{pet}/{expr}: {n} frames")
    with open(os.path.join(HERE, "pip-anim", "index.json"), "w") as fh:
        json.dump(index, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
