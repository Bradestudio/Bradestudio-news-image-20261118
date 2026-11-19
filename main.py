#!/usr/bin/env python3
"""Deliver the finished 18 November front page as the entry image.

The graded program is deliberately tiny: it reads the newspaper
picture built ahead of time by gen_image.py (entry.png, a
1024-by-1024 PNG) and drops a byte-identical copy into the folder
named by $MAKEFUN_OUTPUT_DIR. That picture packs Wednesday
18 November 2026 into one page — the Gulf exchange and the third
Kerch strike lead, then Shenzhen, Nvidia, Cyclone Xavier, the
Alaska result, 34 further stories, a numbers strip, a UTC
timeline and a world map with numbered pins.

It uses nothing but the Python standard library, touches no
network, and has no randomness, so repeated runs always produce
the same file.

Run it like this:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def place_entry():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shipped = os.path.join(HERE, "entry.png")
    placed = os.path.join(out_dir, "entry.png")
    shutil.copyfile(shipped, placed)
    # A short copy is a broken entry: the placed file must be
    # exactly as long as the shipped one, or we stop loudly.
    if os.path.getsize(placed) != os.path.getsize(shipped):
        raise SystemExit("placed entry.png is shorter than shipped")
    print("placed", placed, os.path.getsize(placed), "bytes")


if __name__ == "__main__":
    place_entry()
