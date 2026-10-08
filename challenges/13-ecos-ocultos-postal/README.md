# 13. Ecos Ocultos: Postal

**Category**: Forense (FORENSIC)
**Difficulty**: EASY
**Points**: 100

## Description

> Interceptamos una postal digital: una familia de carpinchos tomando sol en el río. A simple vista es solo una foto bonita, pero las imágenes guardan más de lo que muestran.
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

```bash
$ file postal.png
postal.png: PNG image data, 1280 x 854, 8-bit/color RGB, non-interlaced

$ exiftool postal.png
...
Comment                         : RVZJTHtsMHYzX2M0cHliNHI0fQ==
Title                           : postal
Series                          : Ecos Ocultos
```

The PNG contains a `Comment` field (tEXt chunk) with a base64-encoded string.

## Analysis

The Comment field value `RVZJTHtsMHYzX2M0cHliNHI0fQ==` decodes from base64 to reveal the flag directly.

```bash
$ echo "RVZJTHtsMHYzX2M0cHliNHI0fQ==" | base64 -d
EVIL{l0v3_c4pyb4r4}
```

No trailing data after IEND chunk, no embedded files, no LSB steganography needed. The flag was in plain sight in the metadata.

## Recovery

```python
import base64
comment = "RVZJTHtsMHYzX2M0cHliNHI0fQ=="
flag = base64.b64decode(comment).decode()
print(flag)  # EVIL{l0v3_c4pyb4r4}
```

## Flag

```
EVIL{l0v3_c4pyb4r4}
```

## Key Takeaways

- Always check image metadata (exiftool) first — flags are often hidden in plain sight in tEXt/zTXt chunks.
- Base64-encoded strings in PNG comments are a common easy stego technique.
- The challenge description "las imágenes guardan más de lo que muestran" hints at metadata.

