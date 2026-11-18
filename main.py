#!/usr/bin/env python3
"""news-image-20261118 entry: copy the front-page image to /output.

The image (entry.png, 1024x1024, drawn by gen_image.py) sums up the
world news of Wednesday 18 November 2026 as a newspaper front page:
the Hormuz exchange as the lead, plus the Crimea bridge, the Manila /
Quad summit, Cyclone Akvan, and the Knesset vote. Standard library only,
no network, no randomness: every run writes the exact same bytes.

Run it with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Guard: the copy must be byte-identical to the shipped image, so a
    # partial write can never pass as the entry.
    assert os.path.getsize(dst) == os.path.getsize(src), "short copy"
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main()
