# 17. El puente del paseo

> **Status: unsolved** — the platform rejected the candidate below. No confirmed flag.

**Category**: OSINT  
**Difficulty**: EASY  
**Points**: 150

## Description

> Encontraste esta foto en una red social. La persona que la subió solo escribió: "Hermoso día en la costanera".
> 
> Tu misión es descubrir el nombre del puente que se ve al fondo.
> Objetivo: Identificar el puente.
> **Formato de flag:** `EVIL{puente_xxxxxx_xxxxxxxx}`

## Metadata Analysis

```bash
$ exiftool -a -u -g puente.jpg
```

**Relevant findings (verbatim from exiftool):**

- **File Type**: JPEG
- **Image Size**: 1200×1200 (square)
- **Encoding Process**: Progressive DCT, Huffman coding
- **Orientation**: Horizontal (normal)
- **Resolution**: 72 DPI (X and Y)
- **Color Space**: Uncalibrated (65535)
- **EXIF Version**: 0210
- **Flashpix Version**: 0100
- **No GPS coordinates**, no camera model, no software tag, no timestamps
- **No C2PA/JUMBF blocks** (unlike challenges #16 and #18)
- **No Artist, Copyright, or User Comment fields**

**Conclusion**: The metadata is stripped to minimal EXIF (dimensions, orientation, resolution, color space). The image provides **no forensic geolocation data**. The absence of C2PA metadata means AI-generation cannot be confirmed or ruled out from metadata alone, though the square 1200×1200 format is consistent with AI output.

## Visual Analysis

The image (square 1200×1200) shows a costanera (waterfront promenade) scene with a prominent bridge in the background. Visual indicators:

- Water body in foreground (river/lagoon)
- Costanera walkway with railings, lighting
- **Distinctive suspension bridge** with two tall towers and cable stays spanning the background
- Bridge connects two landmasses across a wide water body
- Clear daytime lighting, consistent with "Hermoso día" caption

**Bridge architecture**: Two-pylon suspension bridge with vertical suspenders, main cables anchored at both ends — classic "puente colgante" silhouette.

**Limitation**: As a static image (potentially AI-generated), visual matching to a real bridge is subjective. No measurements, EXIF focal length, or perspective metadata exist to constrain identification.

## Attribution & Reasoning

**Primary visual candidate: Puente Colgante de Santa Fe (Puente Ingeniero Marcial Candioti)**

Evidence *for* this candidate:
1. **"Costanera" + Argentina**: The term "costanera" is used in several Argentine cities (Buenos Aires, Santa Fe, Posadas, Corrientes, Rosario). The challenge explicitly says "en la costanera".
2. **Santa Fe's Costanera**: Santa Fe has two costaneras (Oeste and Este) bordering Laguna Setúbal, connected by the Puente Colgante — a suspension bridge that is the defining landmark visible from the waterfront.
3. **Flag format**: `EVIL{puente_xxxxxx_xxxxxxxx}` — two words with underscores. "puente_colgante" fits the pattern (12 + 9 chars between braces).
4. **Challenge #16 context**: Same CTF, Argentine theme. Challenge #16's inferred city was Santa Fe (though that candidate was also rejected).

Evidence *against* / gaps:
- **No geolocation metadata** in the image to corroborate
- **Visual match is subjective** — suspension bridges share similar silhouettes globally
- **Alternative Argentine suspension bridges exist** (e.g., Puente Rosario-Victoria is cable-stayed, not suspension; Puente Zárate-Brazo Largo is cable-stayed highway bridge)
- **The platform rejected `puente_colgante` (wrapped in standard flag format)** — this candidate is not the accepted answer

**No bridge can be definitively confirmed from the available evidence.** The earlier candidate was a visually plausible hypothesis, not a verified identification.

## Rejected candidate

The candidate `puente_colgante` (wrapped in standard flag format) was submitted and rejected.

**Platform verdict**: `incorrect` (returned by `/api/v1/challenges/17/submit`).  
**Reason for rejection**: The flag was a visual hypothesis (suspension bridge on Argentine costanera → Santa Fe's Puente Colgante), not a verified identification. The image provides no forensic proof of location.

## Flag

No confirmed flag. The artifact provides no geolocation metadata; visual bridge matching is not verifiable.

## Key Takeaways

- "Costanera" in Argentine context implies several cities; visual bridge matching without metadata is unreliable
- Flag format `puente_xxxxxx_xxxxxxxx` suggests a two-word name, but is a hint — not evidence
- Minimal EXIF (no GPS, no camera, no software) prevents forensic geolocation
- Cross-challenge geographic consistency (Santa Fe theme) is a **hypothesis generator**, not evidence
- **Always verify candidate flags against the platform** — visual plausibility ≠ correct answer

## References

- [Puente Colgante de Santa Fe — Wikipedia](https://es.wikipedia.org/wiki/Puente_Colgante_de_Santa_Fe) — "conectando la Costanera Oeste con la Este"
- [Turismo Santa Fe — Puente Colgante](https://turismo.santafeciudad.gov.ar/puente-colgante) — Official tourism source
- [C2PA Specification](https://c2pa.org/specifications/) — for comparison with challenges #16/#18 metadata

(End of file - total 87 lines)