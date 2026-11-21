#!/usr/bin/env python3
"""Entry for make.fun's "The Passport Page of a Country That Isn't There".

Writes one image, /output/entry.png: an open passport spread of the
Republic of Sorellia, an invented Mediterranean island republic.

The artwork (artwork.png, beside this file) was drawn by render.py from
an original generated portrait; this program is the part the grader
runs, so it uses nothing outside the Python standard library and no
network: it reads the artwork, verifies that it is a whole PNG inside
the competition's caps (at most 1024x1024 pixels and 1,048,576 bytes),
and writes it to /output/entry.png byte for byte, so two runs always
produce the same file.
"""

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARTWORK = os.path.join(HERE, "artwork.png")
MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_artwork(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("artwork is not a PNG")
    if data[12:16] != b"IHDR":
        raise ValueError("artwork's first chunk is not IHDR")
    if len(data) > MAX_BYTES:
        raise ValueError("artwork exceeds the 1 MiB cap: %d bytes" % len(data))
    # IHDR is the first chunk: width and height are big-endian uint32
    # at fixed offsets 16 and 20 in the file.
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("artwork exceeds 1024x1024: %dx%d" % (width, height))
    return data, width, height


def main():
    data, width, height = read_artwork(ARTWORK)
    out_dir = os.environ.get("ENTRY_OUT_DIR", "/output")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%dx%d, %d bytes)" % (out_path, width, height, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
