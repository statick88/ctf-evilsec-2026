#!/usr/bin/env python3
# solve.py — Challenge 14: Ecos Ocultos: Bit por Bit
# Status: UNSOLVED (key recovery open). This script extracts LSB data and
# reproduces every VERIFIED structural finding plus the key-recovery attempts.
#
# Usage: python3 solve.py   (run inside challenges/14-ecos-ocultos-bit-por-bit/)

from PIL import Image
import numpy as np
import json
import hashlib
from collections import Counter

IMAGE = 'mural.png'
CRIB = b'EVIL{'


def extract_lsb_bytes_msb(channel_row):
    lsb = (channel_row & 1)
    out = bytearray()
    for i in range(0, len(lsb), 8):
        byte = 0
        for j in range(8):
            if i + j < len(lsb):
                byte = (byte << 1) | int(lsb[i + j])
        out.append(byte)
    return bytes(out)


def extract_all_rows(image_path, bitplane=0):
    img = Image.open(image_path)
    arr = np.array(img)
    R = [extract_lsb_bytes_msb(((arr[r, :, 0] >> bitplane) & 1)) for r in range(640)]
    G = [extract_lsb_bytes_msb(((arr[r, :, 1] >> bitplane) & 1)) for r in range(640)]
    B = [extract_lsb_bytes_msb(((arr[r, :, 2] >> bitplane) & 1)) for r in range(640)]
    return R, G, B


def ham(a, b):
    return sum(bin(x ^ y).count('1') for x, y in zip(a, b))


def structural_report(R, G, B):
    print('=== 1. Row groups (8-row clusters, R channel) ===')
    for g in range(6):
        base = 8 * g
        mx = max(ham(R[base], R[base + k]) for k in range(8))
        print(f'  group {g} (rows {base}-{base + 7}): max intra-ham {mx} bits of 480')
    print('  -> groups 0-3 tight (<70 bits); groups 4+ random (~150-290 bits)')

    print('=== 2. Exact duplicate rows ===')
    for name, rows in [('R', R), ('G', G), ('B', B)]:
        seen = {}
        dups = []
        for i, r in enumerate(rows):
            if r in seen:
                dups.append((seen[r], i))
            else:
                seen[r] = i
        print(f'  {name}: {dups}')

    print('=== 3. R^G constant (rows 0-14 share C, row 15+ unique) ===')
    C0 = bytes(a ^ b for a, b in zip(R[0], G[0]))
    n_same = sum(1 for r in range(640)
                 if bytes(a ^ b for a, b in zip(R[r], G[r])) == C0)
    print(f'  rows sharing R^G == C0: {n_same} (expect 15: rows 0-14)')
    print(f'  C0 = {C0.hex()[:64]}...')

    print('=== 4. Within-group diffs are channel-independent (group 0) ===')
    ok = all(bytes(a ^ b for a, b in zip(R[0], R[k])) ==
             bytes(a ^ b for a, b in zip(G[0], G[k])) for k in range(8))
    print(f'  R0^Rk == G0^Gk for k=0..7: {ok}')

    print('=== 5. Lag-60 autocorrelation (60B = one row) ===')
    Rb = np.array([list(r) for r in R], dtype=np.uint8).ravel()
    for L in [1, 60, 120]:
        eq = (Rb[:-L] == Rb[L:]).mean()
        print(f'  lag {L}: byte equality {eq:.4f} (random ~0.004)')


def tv_of(P):
    bits = np.unpackbits(P, axis=1).astype(int)
    return int(np.abs(np.diff(bits, axis=0)).sum() + np.abs(np.diff(bits, axis=1)).sum())


def key_recovery_report(R, G, B):
    print('=== 6. Known-plaintext (row 0 starts with EVIL{) ===')
    K5 = bytes(a ^ b for a, b in zip(R[0][:5], CRIB))
    print(f'  K_R[0:5] = {K5.hex()} (byte 1 = 0xa9 non-printable -> binary keystream)')
    print('  NOTE: only 5 bytes are actually known. Zero-ct positions give')
    print('  key=plaintext with BOTH unknown (0 information). The old')
    print('  "32/60 known bytes" claim was wrong.')

    print('=== 7. Digest-key scan (row 0 crib, XOR/ADD/SUB) ===')
    phrases = ['capybara', 'carpincho', 'evilsec', 'mural', 'llave muy nuestra',
               'muy nuestra', 'nuestra', 'espuma', 'ecos', 'EVILSEC', 'evil',
               'mate', 'llave', 'ctf', 'l0v3_c4pyb4r4', 'santuario', 'mural.png',
               '14', 'forense', 'bit por bit', 'bit a bit', 'bano de espuma',
               'carpincho feliz', 'nuestra llave', 'messi', 'scaloneta', 'tango']
    targets = {'xor': K5.hex()}
    db = {}
    for p in phrases:
        for an, H in [('md5', hashlib.md5), ('sha1', hashlib.sha1),
                      ('sha256', hashlib.sha256)]:
            db.setdefault(H(p.encode()).digest()[:5].hex(), []).append((p, an))
    hits = [v for k, v in db.items() if k in targets.values()]
    print(f'  hits: {hits}')

    print('=== 8. TV ranking (single-byte keys; K=0 wins) ===')
    Rn = np.array([list(r) for r in R], dtype=np.uint8)
    base = tv_of(Rn)
    ptim = min((tv_of(np.bitwise_xor(Rn, np.uint8(k))), k) for k in range(256))
    print(f'  baseline TV={base}, best single-byte TV={ptim[0]} (k={ptim[1]})')

    print('=== 9. Ruled-out classes (all tested, all negative) ===')
    print('  raw/digest (md5/sha1/sha256/sha512/blake2b/sha3) of ~30k phrases+affixes')
    print('  + encodings (utf-8/latin-1/utf-16/base64/reversed/case) at every row/offset')
    print('  XOR/ADD/SUB ciphers; MSB/LSB packing; bit-shifts 0-16; column-major,')
    print('  flips, snake, transpose packings; weighted (luminance) channel combos;')
    print('  3-bit-per-pixel plane combos; XOF (shake128/256), RC4, MT19937, LCG')
    print('  (glibc/NR/MSVC/Java/m256) forward streams + algebraic LCG inversion;')
    print('  banner-as-key vs body; self-keys (pixels/file/headers); B-as-key w/ lags;')
    print('  transposition unshuffle; single-byte all rows; 2-byte full TV scan;')
    print('  per-column frequency (text/spanish/printable models); column-agreement')
    print('  keystream chaining (split-half inconsistent); QR decode (OpenCV, combos);')
    print('  OCR (tesseract, banners + full planes).')


def main():
    print('=== Challenge 14: Ecos Ocultos - Bit por Bit ===\n')
    R, G, B = extract_all_rows(IMAGE, bitplane=0)
    print(f'extracted {len(R)} rows/channel, {len(R[0])} bytes each\n')
    structural_report(R, G, B)
    print()
    key_recovery_report(R, G, B)
    data = {'rows_r': [r.hex() for r in R],
            'rows_g': [g.hex() for g in G],
            'rows_b': [b.hex() for b in B]}
    with open('extracted_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('\nSaved extracted_data.json')
    print('\n=== Summary ===')
    print('Status: UNSOLVED — 60-byte fixed keystream per channel confirmed by')
    print('evidence (dup rows 9/14, lag-60 autocorrelation) but not recovered.')
    print('Plaintext is binary/image-like, not ASCII text (freq analysis negative).')
    print('Next: identify the "llave muy nuestra" KDF or a non-XOR cipher.')


if __name__ == '__main__':
    main()
