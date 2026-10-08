#!/usr/bin/env python3
# solve.py — Challenge 14: Ecos Ocultos: Bit por Bit
# LSB steganography in R/G channels with 60-byte period XOR encryption.

from PIL import Image
import numpy as np
from collections import Counter
import re

def extract_lsb_bytes(channel):
    lsb = (channel & 1).flatten()
    bytes_data = bytearray()
    for i in range(0, len(lsb), 8):
        byte = 0
        for j in range(8):
            if i + j < len(lsb):
                byte = (byte << 1) | lsb[i + j]
        bytes_data.append(byte)
    return bytes_data

def solve():
    img = Image.open('mural.png')
    arr = np.array(img)
    
    r_bytes = extract_lsb_bytes(arr[:, :, 0])
    g_bytes = extract_lsb_bytes(arr[:, :, 1])
    
    period = 60
    ct = r_bytes[:period]  # First period (cleanest)
    
    # Known plaintext
    known = {0: ord('E'), 1: ord('V'), 2: ord('I'), 3: ord('L'), 4: ord('{'), 59: ord('}')}
    
    # Derive key from first period
    key = bytearray(period)
    for pos, pt in known.items():
        key[pos] = ct[pos] ^ pt
    
    # Key bytes known: [0]=E, [1]=©(0xa9), [2]=E, [3]=@, [4]={, [59]=}
    # At positions where ct==0x00, key == plaintext (flag)
    # ct==0x00 at: 0,4,8,13,18,19,20,21,28,29,30,31,32,33,34,35,36,37,39,40,43,44,52,57,58,59 (26 positions)
    
    # Reconstruct flag at ct==0x00 positions
    flag = bytearray(b'_' * period)
    for i in range(period):
        if i in known:
            flag[i] = known[i]
        elif ct[i] == 0x00:
            flag[i] = key[i]  # key = plaintext here
    
    flag_text = flag.decode('ascii', errors='replace')
    
    # Also verify G channel gives same key prefix
    ct_g = g_bytes[:period]
    key_g = bytearray(period)
    for pos, pt in known.items():
        key_g[pos] = ct_g[pos] ^ pt
    assert key[:6] == key_g[:6], "R/G key mismatch"
    
    return (f"EVIL{{...}} (partial: {flag_text}) — "
            f"60-byte period, R/G share key, key_prefix=E©E@{{, key[59]='}}', "
            f"26 flag chars at ct=0x00 positions, needs full key recovery")

if __name__ == '__main__':
    result = solve()
    print(result)
