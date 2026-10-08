#!/usr/bin/env python3
# solve.py — Challenge 14: Ecos Ocultos: Bit por Bit
# LSB steganography in R/G channels with per-row 60-byte XOR encryption.
# Extracts all 640 rows from R, G, B channels and attempts key recovery.

from PIL import Image
import numpy as np
import json

def extract_lsb_bytes_msb(channel_row):
    """Extract LSB from a row using MSB-first bit order."""
    lsb = (channel_row & 1)
    bytes_data = bytearray()
    for i in range(0, len(lsb), 8):
        byte = 0
        for j in range(8):
            if i + j < len(lsb):
                byte = (byte << 1) | lsb[i + j]
        bytes_data.append(byte)
    return bytes_data

def extract_all_rows(image_path):
    """Extract per-row ciphertext from all three channels."""
    img = Image.open(image_path)
    arr = np.array(img)  # (640, 480, 3)
    
    rows_r = []
    rows_g = []
    rows_b = []
    
    for row_idx in range(640):
        r_bytes = extract_lsb_bytes_msb(arr[row_idx, :, 0])
        g_bytes = extract_lsb_bytes_msb(arr[row_idx, :, 1])
        b_bytes = extract_lsb_bytes_msb(arr[row_idx, :, 2])
        
        rows_r.append(bytes(r_bytes))
        rows_g.append(bytes(g_bytes))
        rows_b.append(bytes(b_bytes))
    
    return rows_r, rows_g, rows_b

def analyze_row_0(rows_r, rows_g):
    """Analyze first row for known-plaintext attack."""
    ct_r = rows_r[0]
    ct_g = rows_g[0]
    period = 60
    
    print("=== Row 0 Analysis ===")
    print(f"R ciphertext: {ct_r.hex()}")
    print(f"G ciphertext: {ct_g.hex()}")
    print()
    
    # Known plaintext: EVIL{...}
    known = {0: ord('E'), 1: ord('V'), 2: ord('I'), 3: ord('L'), 4: ord('{'), 59: ord('}')}
    
    # Derive key from R channel
    key_r = bytearray(period)
    for pos, pt in known.items():
        key_r[pos] = ct_r[pos] ^ pt
    
    print("Key from R (known positions):")
    for i in range(period):
        if i in known:
            ch = chr(key_r[i]) if 32 <= key_r[i] < 127 else '?'
            print(f"  key[{i:2d}] = 0x{key_r[i]:02x} ({ch})")
    
    # Zero ciphertext positions in R
    zero_pos = [i for i in range(period) if ct_r[i] == 0x00]
    print(f"\nZero ciphertext positions ({len(zero_pos)}): {zero_pos}")
    
    # At zero positions, key = plaintext
    print("\nKey = plaintext at zero positions:")
    for i in zero_pos:
        ch = chr(key_r[i]) if 32 <= key_r[i] < 127 else '?'
        print(f"  key[{i:2d}] = 0x{key_r[i]:02x} ({ch})")
    
    # Partial flag reconstruction
    flag = bytearray(b'_' * period)
    for i in range(period):
        if i in known:
            flag[i] = known[i]
        elif ct_r[i] == 0x00:
            flag[i] = key_r[i]
    
    print(f"\nPartial flag: {flag.decode('ascii', errors='replace')}")
    
    # G channel key at known positions
    key_g = bytearray(period)
    for pos, pt in known.items():
        key_g[pos] = ct_g[pos] ^ pt
    
    print("\nKey from G (known positions):")
    for i in range(period):
        if i in known:
            ch = chr(key_g[i]) if 32 <= key_g[i] < 127 else '?'
            print(f"  key[{i:2d}] = 0x{key_g[i]:02x} ({ch})")
    
    # R^G XOR for row 0
    xor_rg = bytes(a ^ b for a, b in zip(ct_r, ct_g))
    print(f"\nR ^ G XOR (row 0): {xor_rg.hex()}")
    
    return key_r, xor_rg

def test_key_hypotheses(key_r, period):
    """Test candidate key phrases."""
    print("\n=== Key Hypothesis Testing ===")
    
    # Known key bytes
    known_key = {i: key_r[i] for i in range(period) if key_r[i] != 0 or i in [0,1,2,3,4,59]}
    print(f"Known key bytes: {len(known_key)}/60")
    
    phrases = [
        b'capybara',
        b'capybara capybara',
        b'evilsec',
        b'evilsecctf',
        b'evilsec evilsec',
        b'muy nuestra',
        b'llave muy nuestra',
        b'llave muy nuestra llave',
        b'bubble bath',
        b'bubblebath',
        b'bath time',
        b'capybara bubble bath',
        b'bano de espuma',
        b'banio de espuma',
        b'evil{',
        b'EVIL{',
        b'EVILSEC',
        b'evilsecEVILSEC',
    ]
    
    for phrase in phrases:
        key = (phrase * (period // len(phrase) + 1))[:period]
        match = True
        for i, k in known_key.items():
            if key[i] != k:
                match = False
                break
        if match:
            print(f"MATCH: {phrase}")
            flag = bytes(key_r[i] ^ key[i] for i in range(period))
            print(f"  Flag: {flag}")
            print(f"  Flag (ascii): {flag.decode(errors='replace')}")

def find_constant_xor_rows(rows_r, rows_g):
    """Find rows where R^G XOR is constant."""
    print("\n=== R^G XOR Pattern Analysis ===")
    
    xor_groups = {}
    for row in range(640):
        xor_bytes = bytes(a ^ b for a, b in zip(rows_r[row], rows_g[row]))
        if xor_bytes not in xor_groups:
            xor_groups[xor_bytes] = []
        xor_groups[xor_bytes].append(row)
    
    print(f"Unique R^G XOR patterns: {len(xor_groups)}")
    for xor_bytes, rows in sorted(xor_groups.items(), key=lambda x: -len(x[1])):
        print(f"  {len(rows)} rows: {rows[:20]}{'...' if len(rows)>20 else ''}")
        if len(rows) > 1:
            print(f"    XOR: {xor_bytes.hex()}")

def attempt_decrypt_all_rows(rows_r, rows_g, key_r, xor_rg):
    """Attempt to decrypt all rows assuming row 0 key and constant R^G for rows 0-14."""
    print("\n=== Multi-Row Decryption Attempt ===")
    
    # For rows 0-14: G_ct = R_ct ^ xor_rg (constant)
    # So if we have key for R, we can get plaintext for R
    # Plaintext_R = R_ct ^ key_R
    # For rows 0-14, same plaintext? Or different?
    
    period = 60
    results = []
    
    for row in range(min(15, len(rows_r))):
        ct_r = rows_r[row]
        pt_r = bytes(ct_r[i] ^ key_r[i] for i in range(period))
        print(f"Row {row:3d}: {pt_r.decode('ascii', errors='replace')}")
        results.append(pt_r)
    
    # Check if plaintexts are identical
    if len(set(results)) == 1:
        print("\nAll rows 0-14 have IDENTICAL plaintext!")
        flag = results[0]
        print(f"Flag candidate: {flag.decode('ascii', errors='replace')}")
    else:
        print("\nRows 0-14 have DIFFERENT plaintexts")
        # Flag might be split across rows
    
    return results

def main():
    print("=== Challenge 14: Ecos Ocultos - Bit por Bit ===\n")
    
    rows_r, rows_g, rows_b = extract_all_rows('mural.png')
    print(f"Extracted {len(rows_r)} rows per channel (60 bytes each)")
    print(f"R channel sample (row 0): {rows_r[0].hex()[:80]}...")
    print(f"G channel sample (row 0): {rows_g[0].hex()[:80]}...")
    print(f"B channel sample (row 0): {rows_b[0].hex()[:80]}...")
    print()
    
    # Analyze row 0
    key_r, xor_rg = analyze_row_0(rows_r, rows_g)
    
    # Test key hypotheses
    test_key_hypotheses(key_r, 60)
    
    # Find constant XOR rows
    find_constant_xor_rows(rows_r, rows_g)
    
    # Attempt multi-row decryption
    attempt_decrypt_all_rows(rows_r, rows_g, key_r, xor_rg)
    
    # Save extracted data for external analysis
    print("\n=== Saving extracted data ===")
    data = {
        'rows_r': [r.hex() for r in rows_r],
        'rows_g': [r.hex() for r in rows_g],
        'rows_b': [r.hex() for r in rows_b],
        'key_r_partial': key_r.hex(),
        'xor_rg_row0': xor_rg.hex(),
    }
    with open('extracted_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Saved to extracted_data.json")
    
    # Final summary
    print("\n=== Summary ===")
    print("Status: Key recovery incomplete")
    print("Partial flag (row 0): EVIL{_______________________________}")
    print("Known key bytes: 32/60 (6 from flag format + 26 from zero-ciphertext)")
    print("Next: Determine key derivation from image/context")

if __name__ == '__main__':
    main()