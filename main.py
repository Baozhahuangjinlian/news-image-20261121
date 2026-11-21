#!/usr/bin/env python3
"""Entry point for the 21 November 2026 one-day news image.

The front page is pre-rendered in entry.png (a 1024x1024 PNG drawn
with PIL from the day's verified stories). This program's only job is
to place an exact copy of that image at the grader's output path and
to prove the copy is intact before it exits.
"""

import hashlib
import os
import shutil
import struct
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576


def fail(message):
    print(f"main.py: {message}", file=sys.stderr)
    return 1


def inspect(path):
    """Read the image header and return (width, height, byte count)."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if len(head) < 33 or head[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG file (bad signature)")
    if head[12:16] != b"IHDR":
        raise ValueError("not a PNG file (first chunk is not IHDR)")
    width, height = struct.unpack(">II", head[16:24])
    return width, height, os.path.getsize(path)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")

    width, height, size = inspect(SOURCE)
    if (width, height) != (1024, 1024):
        return fail(f"entry.png is {width}x{height}, expected 1024x1024")
    if size > MAX_BYTES:
        return fail(f"entry.png is {size} bytes, over the 1 MiB limit")

    shutil.copyfile(SOURCE, target)

    with open(SOURCE, "rb") as a, open(target, "rb") as b:
        if hashlib.sha256(a.read()).hexdigest() != hashlib.sha256(b.read()).hexdigest():
            return fail("output bytes differ from entry.png")

    out_w, out_h, out_size = inspect(target)
    if (out_w, out_h) != (1024, 1024) or out_size != size:
        return fail("output failed its post-copy check")

    print(f"wrote {target} ({out_w}x{out_h}, {out_size} bytes, sha256 verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
