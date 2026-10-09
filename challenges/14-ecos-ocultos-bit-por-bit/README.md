# 14. Ecos Ocultos: Bit por Bit

**Category**: Forense (FORENSIC)  
**Difficulty**: MEDIUM  
**Points**: 250  

## Description

> Un carpincho disfrutando su baño de espuma. La imagen parece completamente normal, pero la verdad se esconde en los bits más pequeños. No todos los colores pesan igual, y lo que encuentres va a estar protegido con una llave muy nuestra.
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

```bash
$ file mural.png
mural.png: PNG image data, 480 x 640, 8-bit/color RGB, non-interlaced

$ exiftool mural.png
# No suspicious metadata, no Comment field

$ binwalk mural.png
# No embedded files
```

## Analysis

### Image Structure

- Dimensions: 480 × 640 pixels
- Channels: RGB (3 channels × 8-bit)
- Total pixels per channel: 307,200
- LSB capacity per channel: 307,200 bits = 38,400 bytes

### LSB Extraction

Extracting LSB from each channel (MSB-first bit order within each byte):

| Channel | LSB 1s / Total | Percentage |
|---------|----------------|------------|
| R       | 156,289 / 307,200 | 50.88% |
| G       | 156,288 / 307,200 | 50.88% |
| B       | 151,396 / 307,200 | 49.28% |

R and G channels show nearly identical LSB distributions; B differs significantly.

### Per-Row Ciphertext Structure

Each row = 480 pixels = 480 bits = **60 bytes per channel**.
Total: 640 rows × 60 bytes = 38,400 bytes per channel.

**Critical discovery**: Each row encodes a **different** 60-byte ciphertext block.
- 639 unique ciphertexts in R channel (rows 0-639, only rows 9&14 identical)
- 639 unique ciphertexts in G channel (rows 0-639, only rows 9&14 identical)
- The "60-byte period" reported earlier was an artifact of analyzing only the first few similar rows.

### R/G Channel Relationship

For rows 0-14: R and G ciphertexts share a **constant XOR relationship**:
```
R_ct ^ G_ct = C (constant 60-byte pattern, verified: exactly 15 rows share C0)
C = 00000000000000007fffffffffffff03c0fffffffffffffffffe0000800000000000000000007fff
```

This implies: `G_ct = R_ct ^ C` for rows 0-14.

For rows 15+: R^G XOR is unique per row (no constant relationship).

**Correction (2026-10-08)**: the earlier claim `R_ct[row] = R_ct[0] ^ row`
(XOR with row index) is FALSE. Verified counter-evidence: `R0^R1` differs in
only 2 bits at positions 41/55, while `R0^R3` differs in 32 bits across 4 full
bytes — no row-index pattern.

### "No todos los colores pesan igual"

- **R and G ("heavy" channels)**: Carry the main payload (640 × 60 bytes each), highly correlated
- **B ("light" channel)**: Different distribution (49.28% ones), likely decoy or different encoding

### "Llave muy nuestra" — Key Derivation

The key is "very ours" — derived from challenge context.

**Hypotheses for key source:**
1. **Image-derived**: Palette colors, dimensions (480×640), statistical properties
2. **Text-derived**: "capybara", "bubble bath", "baño de espuma", "evilsec", "muy nuestra"
3. **Structural**: Row indices, pixel coordinates, LSB statistics

### Encryption Scheme

Evidence suggests **XOR stream cipher** per row:
- Each row: `ciphertext[row] = plaintext[row] ^ keystream[row]`
- Keystream likely derived from master key + row index
- R and G may use same keystream with constant offset (rows 0-14)

### Known-Plaintext Attack (Row 0)

Assuming flag format `EVIL{...}` (60 bytes) in row 0:

**R channel (row 0) ciphertext:**
```
00 ff 0c 0c 00 ff ff ff 00 ff ff ff ff 00 03 fa be dc 00 00 00 00 ff ff e3 67 47 8f 00 00 00 00 00 00 00 00 00 00 71 00 00 1c ff 00 00 03 36 e3 ff ff ff ff 00 ff ff 38 ff 00 00 00
```

**Known plaintext positions (flag format):**
| Pos | Plaintext | R_ct | Key = ct ^ pt |
|-----|-----------|------|---------------|
| 0   | 'E' (0x45) | 0x00 | 0x45 |
| 1   | 'V' (0x56) | 0xff | 0xa9 |
| 2   | 'I' (0x49) | 0x0c | 0x45 |
| 3   | 'L' (0x4c) | 0x0c | 0x40 |
| 4   | '{' (0x7b) | 0x00 | 0x7b |
| 59  | '}' (0x7d) | 0x00 | 0x7d |

**Key prefix (row 0):** `45 a9 45 40 7b` → `E` `©` `E` `@` `{`

**Zero-ciphertext positions in row 0 (26 positions):**
```
[0, 4, 8, 13, 18, 19, 20, 21, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 43, 44, 52, 57, 58, 59]
```
At these positions `key = plaintext`, but BOTH are unknown, so this yields
**zero** information. Correction (2026-10-08): the old "32/60 known bytes"
claim was wrong — only the 5 crib bytes above are actually known (the `}` at
59 assumes a 60-char flag and is itself uncertain).

### Key Recovery Challenge

Only 5 of 60 key bytes are known (crib `EVIL{` at row 0). The keystream is
binary (byte 1 = 0xa9 rules out any raw printable-phrase key).

**Key properties observed:**
- Non-ASCII byte at position 1 (0xa9 = ©) → keystream is binary, NOT a raw phrase
- Fixed 60-byte keystream per channel (evidence: exact duplicate rows 9/14 in
  all channels; lag-60 byte autocorr 0.21-0.25 vs 0.004 random)
- Plaintext is binary/image-like, NOT ASCII text (per-column frequency analysis
  with Spanish/printable models yields garbage, ~0.43 printable ≈ random)
- Bit planes 0, 1, 2 are ALL synthetic (author-written) in all three channels

**Key-search status (2026-10-08, all negative):** raw/digest
(md5/sha1/sha256/sha512/blake2b/sha3) of ~30k phrases + affixes + encodings
(utf-8/latin-1/utf-16/base64/reversed/case) at every row/offset for XOR/ADD/SUB;
MSB/LSB packing; bit-shifts; column-major/flips/snake/transpose; weighted
(luminance) combos; 3-bit plane combos; XOF (shake128/256), RC4, MT19937, LCG
(glibc/NR/MSVC/Java/m256, forward + algebraic inversion vs crib); banner-as-key;
self-keys (pixels/file/headers/hashes); B-as-key incl. all lags; transposition
unshuffle; single-byte (all rows) and full 2-byte TV scans (K=0 wins);
column-agreement keystream chaining (split-half inconsistent); G-key-from-C
algebra (needs a crib that does not exist for image plaintext).

### Row 0 Decryption Attempt

Row 0 cannot be decrypted: only 5 key bytes are known and the plaintext is
binary (image-like), so there is no `EVIL{...}` text at a known offset to
extend the key. The old partial-flag diagram is retired.

## Exploitation / Recovery

### Current Approach

1. **Extract all 640 rows** from R, G, B channels (bit planes 0-2 all carry data)
2. **Keystream structure (verified)**: fixed 60-byte key per channel; rows 0-14
   share R^G constant C; rows 0-31 form 4 tight 8-row groups (banners); rows
   9/14 exactly duplicate in all channels; within-group diffs are
   channel-independent in group 0
3. **Key recovery**: OPEN — the "llave muy nuestra" KDF is unidentified and no
   crib exists (plaintext is not text). Best next leads:
   - non-XOR cipher (e.g. block cipher with post-embedding sync-bit flips, which
     would explain tiny within-group diffs under similar plaintexts);
   - key hidden in a non-obvious image property (e.g. IDAT chunk CRCs, palette
     statistics) rather than a phrase digest;
   - 8x8-glyph structure: within-group whole-byte diffs suggest 8px-aligned
     content — a frequent background glyph would leak K per column
     (untested: per-column dominant-pair analysis + global-flip resolution via
     rendered-text OCR of the two candidate images).
4. **B channel analysis**: B carries the same scheme (same groups/dups/stats),
   not just a decoy; B0 is random-like while B1+ are banner-structured.

### Python Extraction Script

See `solve.py` for extraction + all verified structural checks (runnable,
reports UNSOLVED honestly).

## Flag

```
Status: unsolved — keystream not recovered, no flag submitted.
Platform check: `python3 scripts/lib/ctf_platform.py audit` shows #14 pending.
```

## Key Takeaways

- **Per-row steganography**: Each image row = 60-byte block (row-major,
  MSB-first packing confirmed by 8-row group structure).
- **Fixed keystream, not per-row**: dup rows 9/14 + lag-60 autocorr prove a
  repeating 60-byte key per channel; the old per-row-keystream theory is dead.
- **Plaintext is binary**: frequency analysis rules out ASCII/text plaintext;
  treat it as a 1-bit image, not a flag string (no `EVIL{` cribs exist).
- **Zero-ct positions leak nothing**: key=plaintext with both unknown.
- **Multi-plane embedding**: bit planes 0-2 are all synthetic in R, G and B.
- **Negative results are results**: ~30k-phrase digest space, all standard
  PRNG/LCG/XOF families (forward + inversion), packing variants, and
  structural key recovery (chaining, TV, solid-row) all fail — the KDF is
  non-standard or the cipher is non-XOR.

## References

- LSB steganography: https://en.wikipedia.org/wiki/Steganography#LSB
- XOR stream cipher: https://crypto.stackexchange.com/questions/tagged/stream-cipher
- PNG format: https://www.w3.org/TR/png/