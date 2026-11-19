#!/usr/bin/env python3
"""Entry program: copy the rendered front page to the output directory.

Standard library only. Deterministic: the same bytes are written on every
run, and the copy is verified against the source with a sha256 check.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    with open(SOURCE, "rb") as handle:
        magic = handle.read(len(PNG_MAGIC))
    if magic != PNG_MAGIC:
        print("error: entry.png is not a PNG file", file=sys.stderr)
        return 1
    source_hash = sha256_of(SOURCE)
    shutil.copyfile(SOURCE, dest)
    dest_hash = sha256_of(dest)
    if dest_hash != source_hash:
        print("error: copied file hash does not match source", file=sys.stderr)
        return 1
    size = os.path.getsize(dest)
    print(f"wrote {dest}: {size} bytes, sha256 {dest_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
