# 15. Ecos Ocultos: Ruido Controlado

**Category**: Forense (FORENSIC)
**Difficulty**: HARD
**Points**: 500

## Description

> Una postal de un carpincho con gafas llegó dañada: algunos visores ni siquiera la abren. Alguien la recortó sin borrar nada. Lo que quedó escondido parece ruido… pero no todo el ruido es azar.
>
> No hay contraseñas ni claves: todo se resuelve localmente.
>
> **Formato de flag:** `EVIL{...}`

## Artefacts

- `ruido.png`

## Status: UNSOLVED

## Reconnaissance

```bash
$ file ruido.png
ruido.png: PNG image data, 625 x 350, 8-bit/color RGB, non-interlaced

$ exiftool ruido.png
# No suspicious metadata
```

### Structural Damage
PNG chunk analysis reveals an **IHDR height/CRC mismatch**:

```
IHDR chunk: length=13
  File height:          350
  Stored CRC:           0x706fc708
  CRC if height = 350:  0x65fdde11
  CRC if height = 430:  0x706fc708
```

The stored CRC is not random corruption: it is exactly the CRC for the same IHDR with height **430**. The file was cropped by changing the height from 430 to 350 while leaving the original CRC and all IDAT scanlines in place. This explains "algunos visores ni siquiera la abren" — strict viewers reject the mismatched CRC.

All other chunks (7× IDAT, IEND) have valid CRCs. No trailing data after IEND.

### Hidden Data Discovery
Decompressing all IDAT chunks reveals **806,680 bytes** of decompressed data, but a 350×625 RGB image expects only 656,600 bytes (350 rows × 1876 bytes/row). There are **150,080 extra bytes = 80 full rows** hidden in the IDAT stream.

The original image was **430×625** (350 + 80 rows). The bottom 80 rows were "cropped without deleting" — they remain in the compressed data.

## Repair

The correct repair is to restore IHDR height to 430, which also makes the stored CRC valid:

```python
ihdr_height = 430
correct_crc = zlib.crc32(b'IHDR' + ihdr_data_with_height_430) & 0xffffffff
# 0x706fc708, matching the stored CRC
```

`solve.py` writes `ruido_fixed.png` with height 430 and a standards-correct PNG structure.

## Analysis

### Image Statistics (Repaired, 350×625)
- Dimensions: 625 × 350 RGB
- LSB distribution: ~50% ones in all channels (consistent with noise)
- Spatial correlation: High (smooth gradients), not random

### Noise Structure Discovery
The image is **procedural 8×8 value noise**:
- Grid vertices at every 8 pixels (44×79 corner grid)
- Corner values show smooth 2D variation (coherent noise)
- Pixel values interpolated between grid vertices
- Not random — structured Perlin/value noise

### Corner Grid Analysis
```
Corner grid: 44 rows × 79 cols (350/8≈44, 625/8≈79)
R corners: range 0–240, smooth 2D variation
G corners: range 0–244, smooth 2D variation  
B corners: range 0–245, smooth 2D variation
```

Corner values are the "random" seeds at grid vertices; image is bilinear interpolation.

### Full Image Analysis (430×625, including hidden rows)
Reconstructing the full 430×625 image from all IDAT data reveals **three distinct horizontal bands**:

| Region | Rows | Mean (R/G/B) | Std Dev | Characteristics |
|--------|------|--------------|---------|-----------------|
| Top | 0–79 | ~80 | ~112 | Different noise field |
| Middle | 80–349 | ~113 | ~112 | Main visible image |
| Bottom (hidden) | 350–429 | ~127 | ~74 | **Hidden/cropped portion**, lower variance |

The hidden 80 rows (bottom band) have significantly lower standard deviation (~74 vs ~112), indicating a different noise field or less variation.

### "Alguien la recortó sin borrar nada"
Original noise likely larger; cropped to 350×625. Grid alignment: 625/8=78.125, 350/8=43.75 — not exact multiples, so crop cuts through grid cells.

### "No hay contraseñas ni claves: todo se resuelve localmente"
Seed derivable from image properties:
- Dimensions: 625 × 350 (or 625 × 430 full)
- IHDR CRC (correct): `0x65fdde11`
- IHDR CRC (original corrupt): `0x706fc708`
- File size: 462,910 bytes
- Color statistics (means, std devs)

### G Channel Corner Grid — Permutation Table Evidence
The G channel corner grid uses **all 256 byte values** (0–255), suggesting a permutation table (like Perlin noise):
- 54×79 = 4266 corners, each value appears ~16 times
- Distribution heavily skewed: values 0, 255, 1, 254, 2, 253... appear most frequently
- This indicates a permutation-based hash: `value = perm[(perm[x] + y) % 256]`

### Bitplane Steganography Check

`solve.py` now performs a standards-correct PNG unfilter for all 430 rows. A previous working script used the filtered compressed prior scanline as the predictor for filters 2–4; that invalidated downstream hidden-row images. The corrected decoder matches Pillow when the height is restored to 430.

Current direct extraction status:
- Full image direct bitplanes 0–7, R/G/B/RGB/BGR, big/little bit order: no `EVIL{...}` found
- Visible rows direct bitplanes 0–7: no `EVIL{...}` found
- Hidden rows 350–429 direct bitplanes 0–7: no `EVIL{...}` found
- Common multi-plane orders (`0,1,2`, `7,6,5`, full byte LSB/MSB per channel): no `EVIL{...}` found
- Noise parameters (octaves, persistence, lacunarity): Not directly visible

## Hypothesis

The flag is the **seed** used to generate the procedural noise, or encoded in noise parameters (octaves, persistence, lacunarity, seed). Since "no passwords or keys", the seed must be computable from the image itself (dimensions, CRC, statistics).

Common noise seed candidates to test:
- `625`, `350`, `430`, `625*350=218750`, `625*430=268750`
- `0x65fdde11` (correct IHDR CRC)
- `0x706fc708` (original corrupt CRC)
- Hash of "EVIL{", "carpincho", "mural", "ruido", "ecos"

The corrupted CRC value `0x706fc708` is itself meaningful (intentional corruption). The difference `0x706fc708 ^ 0x65fdde11 = 0x15921b19` may also be relevant.

## Recovery Status

**Unsolved** — Flag not found after corrected 430-row PNG recovery and direct/common bitplane extraction. Noise is procedural-looking value noise with 8×8 grid evidence (44×79 corners for visible 350×625, 54×79 for full 430×625). Seed or generation parameters may be derivable from image properties (dimensions, restored height, CRC), but the encoding is not a direct bitplane flag.

## Flag

```
Status: unsolved
Best hypothesis: Flag = noise seed or encoded in noise parameters
```

## Key Takeaways

- Always validate PNG CRCs — corrupted headers hide data and break viewers
- Procedural noise (value/Perlin) leaves structural fingerprints (grid alignment, smooth corners)
- "No passwords" = seed is in the file metadata (dimensions, CRC, statistics)
- Crop without deletion preserves noise structure; grid alignment reveals original scale
- IDAT chunks can hide extra image rows beyond IHDR dimensions
- Permutation-table noise (Perlin-style) shows non-uniform value distributions

## References

- PNG Specification: https://www.w3.org/TR/png/
- Perlin Noise: https://en.wikipedia.org/wiki/Perlin_noise
- Value Noise: https://en.wikipedia.org/wiki/Value_noise
- PNG CRC: https://www.libpng.org/pub/png/spec/1.2/PNG-CRCAppendix.html