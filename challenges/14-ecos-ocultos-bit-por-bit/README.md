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
R_ct ^ G_ct = C (constant 60-byte pattern)
C = 00000000000000007fffffffffffff03c0fffffffffffffffffe0000800000000000000000007fff
```

This implies: `G_ct = R_ct ^ C` for rows 0-14.

For rows 15+: R^G XOR becomes unique per row (no constant relationship).

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

**Key prefix (row 0):** `45 a9 45 40 7b ... 7d` → `E` `©` `E` `@` `{` ... `}`

**Zero-ciphertext positions in row 0 (26 positions):**
```
[0, 4, 8, 13, 18, 19, 20, 21, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 43, 44, 52, 57, 58, 59]
```
At these positions: `key = plaintext` (since `0 ^ key = key`).

### Key Recovery Challenge

The 60-byte key for row 0 is partially known (6 bytes from flag format, 26 bytes from zero-ciphertext positions = 32 known bytes). Remaining 28 bytes unknown.

**Key properties observed:**
- Non-ASCII byte at position 1 (0xa9 = ©)
- Printable ASCII at known positions: E, @, {, }
- Key appears to be a structured phrase, not random

**Candidate key phrases tested (none matched):**
- "capybara", "evilsec", "muy nuestra", "llave muy nuestra", "bubble bath", "evilsecctf"

### Row 0 Decryption Attempt

With partial key, row 0 plaintext at known positions:
```
EVIL{_______________________________}
 ^   ^                       ^    ^
 0   4                       58   59
```

Zero-ciphertext positions reveal key bytes directly, but most are 0x00 (suggesting either key=0x00 or plaintext=0x00 at those positions — unlikely for text flag).

## Exploitation / Recovery

### Current Approach

1. **Extract all 640 rows** from R and G channels
2. **Identify keystream structure**: Row 0-14 share R^G constant; rows 15+ unique
3. **Key derivation**: Test hypotheses:
   - Key = hash(image properties + row_index)
   - Key = phrase repeated/truncated to 60 bytes
   - Key = derived from pixel statistics per row
4. **Multi-row attack**: Flag may be split across rows, or same flag encrypted 640 ways
5. **B channel analysis**: Check if B channel carries key schedule or metadata

### Python Extraction Script

See `solve.py` for complete extraction of all 640 rows from R, G, B channels.

## Flag

```
Status: unsolved — key recovery incomplete
Partial (row 0): EVIL{_______________________________}
```

The flag is likely in row 0 (or distributed across first N rows). Full key recovery needed.

## Key Takeaways

- **Per-row steganography**: Each image row = independent 60-byte ciphertext block
- **Multi-channel correlation**: R/G share structure with constant XOR (rows 0-14)
- **Not a single period**: Autocorrelation on concatenated stream finds false period
- **Key is contextual**: "Muy nuestra" = derived from challenge/image, not random
- **Zero-ciphertext leaks**: 26/60 positions in row 0 leak key directly
- **B channel is distinct**: 49.28% ones vs 50.88% — confirm payload in R/G only

## References

- LSB steganography: https://en.wikipedia.org/wiki/Steganography#LSB
- XOR stream cipher: https://crypto.stackexchange.com/questions/tagged/stream-cipher
- PNG format: https://www.w3.org/TR/png/