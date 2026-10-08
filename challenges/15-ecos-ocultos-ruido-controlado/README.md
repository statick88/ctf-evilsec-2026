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

## Reconnaissance

```bash
$ file ruido.png
ruido.png: PNG image data, 625 x 350, 8-bit/color RGB, non-interlaced

$ exiftool ruido.png
# No suspicious metadata
```

### Structural Damage
PNG chunk analysis reveals **corrupted IHDR CRC**:

```
IHDR chunk: length=13, CRC=BAD
  Calculated CRC: 0x65fdde11
  Stored CRC:     0x706fc708
```

The IHDR data itself is valid (625×350, 8-bit RGB, color type 2), but the CRC is wrong. This explains "algunos visores ni siquiera la abren" — some viewers reject the file due to CRC mismatch.

All other chunks (7× IDAT, IEND) have valid CRCs. No trailing data after IEND.

## Repair

Fixed IHDR CRC by recalculating:
```python
correct_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff  # 0x65fdde11
```
Repaired PNG (`ruido_repaired.png`) opens normally in all viewers.

## Analysis

### Image Statistics (Repaired)
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

### "Alguien la recortó sin borrar nada"
Original noise likely larger; cropped to 625×350. Grid alignment: 625/8=78.125, 350/8=43.75 — not exact multiples, so crop cuts through grid cells.

### "No hay contraseñas ni claves: todo se resuelve localally"
Seed derivable from image properties:
- Dimensions: 625 × 350
- IHDR CRC (correct): `0x65fdde11`
- IHDR CRC (original corrupt): `0x706fc708`
- File size: 462,910 bytes
- Color statistics (means, std devs)

### LSB Steganography Check
- Full image LSB (all channels): No flag found
- Corner grid LSB: No flag found
- Noise parameters (octaves, persistence, lacunarity): Not directly visible

## Hypothesis

The flag is the **seed** used to generate the procedural noise, or encoded in noise parameters (octaves, persistence, lacunarity, seed). Since "no passwords or keys", the seed must be computable from the image itself (dimensions, CRC, etc.).

Common noise seed candidates to test:
- `625`, `350`, `625*350=218750`, `625+350=975`
- `0x65fdde11` (correct IHDR CRC)
- `0x706fc708` (original corrupt CRC)
- Hash of "EVIL{", "carpincho", "mural", "ruido", "ecos"

## Recovery Status

**Unsolved** — Flag not found in LSB or corner LSB. Noise is procedural value noise with 8×8 grid (44×79 corners). Seed likely derivable from image properties (dimensions, CRC). Requires identifying noise algorithm and reverse-engineering seed.

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

