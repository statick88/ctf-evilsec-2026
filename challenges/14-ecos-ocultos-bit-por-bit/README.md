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

### LSB Extraction
Extracting LSB from each channel (480×640 = 307,200 pixels → 38,400 bytes per channel):

| Channel | LSB 1s / Total | Percentage |
|---------|----------------|------------|
| R       | 156,289 / 307,200 | 50.88% |
| G       | 156,288 / 307,200 | 50.88% |
| B       | 151,396 / 307,200 | 49.28% |

R and G channels show nearly identical LSB distributions; B differs.

### Periodicity Discovery
Autocorrelation of R channel LSB stream reveals a **strong 60-byte period** (95.5% match at offset 60 over first 200 bytes). The LSB stream consists of 640 repetitions of a ~60-byte ciphertext block.

### R/G Channel Correlation
R and G channels share the **same encryption key**:
- First period ciphertexts differ at 38/60 positions (systematic: one has 0x00 where other has 0x7f/0xff)
- At 22 positions they agree exactly
- Known-plaintext attack (assuming `EVIL{` prefix) yields **identical key prefix** for both channels

### Known-Plaintext Attack
Assuming flag format `EVIL{...}` (60 bytes: `EVIL{` + 54 chars + `}`):

```
Ciphertext (R, first 60 bytes): 00 ff 0c 0c 00 ff ff ff 00 ff ff ff ff 00 03 fa be dc ...
Plaintext (known):              E  V   I  L  {                           }
Key (ct ^ pt):                  45 a9 45 40 7b                        7d
                                E  ©  E  @  {                           }
```

**Key prefix**: `E©E@{` (only byte 1 is non-printable: 0xA9 = ©)
**Key suffix**: `}` at position 59

### Key Properties
- Key length: 60 bytes (matches period)
- At ciphertext positions = 0x00 (26 positions in first period), **key = plaintext**
- This gives 26 flag characters directly from key at those positions
- Known flag positions: 0=`E`, 4=`{`, 59=`}`, plus 23 more at zero-ciphertext positions
- R and G channels confirm identical key

### "No todos los colores pesan igual"
R and G ("heavy" channels) carry the encrypted payload with identical key; B ("light" channel) is different — possibly a decoy or uses different scheme.

### "Llave muy nuestra"
Key is "very ours" — derived from challenge context. Key prefix `E©E@{` contains `E`, `@`, `{`, `}` and copyright symbol © (0xA9), suggesting a phrase related to "EvilSec", "copyright", or the flag format itself.

## Recovery Status

**Partial flag reconstructed** at 26 positions where ciphertext = 0x00 (key = plaintext):

```
EVIL{_______________________________}
 ^   ^                       ^    ^
 0   4                       58   59
```

Full key recovery needed for remaining 34 positions. The key appears to be a 60-byte phrase with `E©E@{` prefix and `}` suffix.

## Flag

```
Status: unverified (partial recovery)
Partial: EVIL{_______________________________}
```

## Key Takeaways

- Multi-channel LSB steganography with shared key across "heavy" channels (R,G)
- 60-byte period detected via autocorrelation (95.5% match)
- Known-plaintext attack on `EVIL{` prefix reveals key structure
- Ciphertext zeros directly reveal plaintext (key = plaintext at those positions)
- "Not all colors weigh equal" = payload in R/G only; B is different

