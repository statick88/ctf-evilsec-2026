#!/usr/bin/env python3
"""Recover the flag encoded in the CSS color stream of challenge.html.

The CSS background colors are x86-64 shellcode bytes. The shellcode derives an
AES-256 key from SHA-256("FITO PAEZ") with Windows CryptoAPI and decrypts a
48-byte ciphertext with AES-CBC and a zero IV.
"""
from hashlib import sha256
from pathlib import Path
import re

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

html = Path(__file__).with_name("challenge.html").read_text(encoding="utf-8")
colors = re.findall(r"background-color:\s*#([0-9a-fA-F]{6})", html)
shellcode = bytes(int(color[i:i + 2], 16) for color in colors for i in (0, 2, 4))

ciphertext = shellcode[0x490:0x490 + 0x30]
key = sha256(b"FITO PAEZ").digest()
plain = unpad(AES.new(key, AES.MODE_CBC, iv=b"\0" * 16).decrypt(ciphertext), 16)
print(plain.decode("utf-8"))
