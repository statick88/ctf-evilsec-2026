#!/usr/bin/env python3
"""Decode the zero-width steganographic payload from leyenda_pombero.txt."""
from pathlib import Path

TEXT = Path(__file__).with_name("leyenda_pombero.txt").read_text(encoding="utf-8")
ZWSP = "\u200b"
ZWNJ = "\u200c"

bits = "".join("0" if ch == ZWSP else "1" for ch in TEXT if ch in {ZWSP, ZWNJ})
raw = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits) // 8 * 8, 8))
flag = raw.decode("utf-8")
print(flag)
