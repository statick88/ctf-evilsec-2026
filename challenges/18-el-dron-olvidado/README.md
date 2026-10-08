# 18. El dron olvidado

> **Status: unsolved** — the platform rejected the candidate below. No confirmed flag.

**Category**: OSINT  
**Difficulty**: MEDIUM  
**Points**: 250

## Description

> Un operador de drones subió esta foto a un grupo privado y luego la borró. Solo quedó esta captura. Necesitamos saber el lugar exacto desde donde se tomó (nombre del lugar + ciudad).
> Objetivo: Identificar el lugar.
> **Formato de flag:** `EVIL{nombre_y_ciudad}`

## Metadata Analysis

```bash
$ exiftool -a -u -g dron.jpg
```

**Relevant findings (verbatim from exiftool):**

- **File Type**: JPEG
- **Image Size**: 1168×784 (landscape orientation, ~3:2 aspect ratio — typical drone photo ratio)
- **Encoding Process**: Baseline DCT, Huffman coding
- **Software**: **Grok Imagine** (AI image generator by SpaceXAI/xAI) — same generator as challenge #16
- **C2PA Metadata**: Present — AI-generated content
  - `c2pa.actions.v2`: Action = `c2pa.created`, Software Agent = `Grok Imagine`, Digital Source Type = `trainedAlgorithmicMedia`
  - `c2pa.creative_work`: Author Type = `Organization`, Author Name = `SpaceXAI`
  - `c2pa.hash.data`: SHA-256 hash of pixel data (exclusions: bytes 2156–15616)
  - `c2pa.claim.v2`: Claim Generator = `Grok Imagine 0.0.0`, C2PA Library = `0.76.2`
  - `c2pa.signature`: Self-signed C2PA manifest
- **Artist / UUID**: `528559e4-1700-4133-a71c-11f473dcd999` (different UUID from challenge #16)
- **Image Description** and **User Comment**: Identical base64-encoded cryptographic signature (C2PA assertion hash, different from challenge #16)
- **No GPS coordinates**, no camera model, no real timestamps in standard EXIF
- **No JFIF resolution data** (Resolution Unit = None, X/Y Resolution = 1)

**Conclusion**: The image is **synthetic (AI-generated)**, not a real drone photograph. All metadata confirms generation by Grok Imagine (SpaceXAI). There is **no geolocation data whatsoever** in the file — no GPS, no XMP location, no C2PA location assertions.

## Visual Analysis

The image (landscape 1168×784, ~3:2 drone aspect ratio) depicts an aerial perspective with:

- Water body dominating frame (river or lagoon)
- Green spaces / parks along shoreline
- Urban grid visible in background
- Distinctive peninsula or curved shoreline
- Possible bridge or pier structure
- High detail in vegetation and water texture (AI "drone photo" style)

**Limitation**: As an AI-generated image, these visual elements represent the generator's *interpretation* of a drone photo prompt, not a real geographic location. The model synthesizes generic "drone photo of costanera" features — water, green space, urban grid — without rendering a specific, identifiable place unless explicitly prompted with a location name.

## Attribution & Reasoning

The challenge narrative ("drone photo deleted from private group") and visual style (aerial, water + green space) invite geographic speculation. However:

- **The image is AI-generated** (C2PA: `trainedAlgorithmicMedia`, Software: `Grok Imagine`). It depicts a synthetic scene.
- **No forensic geolocation data exists** in the artifact — no GPS, no camera metadata, no location assertions.
- The **capybara motif** across 6 other challenges (#05, #06, #09, #10, #11, #12) and the "costanera" term in #17 are **thematic correlations**, not evidence in this image.
- Costanera Sur Ecological Reserve (Buenos Aires) is a known capybara habitat and drone photography spot, but **this image does not contain identifiable landmarks** of that reserve (specific lagoon shapes, Puerto Madero skyline, distinctive trail network).
- The earlier candidate `reserva_ecologica_costanera_sur_buenos_aires` (wrapped in standard flag format) was based on **thematic speculation** (capybara motif + costanera term + drone aspect ratio), not on evidence in the challenge artifact. The platform rejected it.

**No location can be asserted from the available evidence.** The artifact is a synthetic drone-style image with no verifiable geographic correspondence.

## Rejected candidate

The candidate `reserva_ecologica_costanera_sur_buenos_aires` (wrapped in standard flag format) was submitted and rejected.

**Platform verdict**: `incorrect` (returned by `/api/v1/challenges/18/submit`).  
**Reason for rejection**: The flag was a hypothesis derived from cross-challenge thematic analysis (capybara motif, "costanera" terminology, drone aspect ratio), not from forensic or visual evidence in the artifact. The image is AI-generated with no geolocation data.

## Flag

No confirmed flag. The artifact is synthetic with no geolocation metadata.

## Key Takeaways

- AI-generated drone images (C2PA/Grok Imagine) **cannot be geolocated** — they depict synthetic scenes prompted by text, not real coordinates
- C2PA metadata (`trainedAlgorithmicMedia`) definitively identifies AI origin; absence of GPS is by design, not a puzzle
- Drone aspect ratio (3:2, 4:3, 16:9) in AI output reflects the *prompted format*, not a real sensor
- Cross-challenge thematic analysis (capybara motif → Costanera Sur) is a **pivot for hypothesis generation**, not evidence for flag submission
- Deleted social media content narrative ("borró la foto") is a story element, not a forensic clue when the image is synthetic
- **Always verify candidate flags against the platform** — thematic plausibility ≠ correct answer

## References

- [Grok Imagine (SpaceXAI)](https://grok.com/imagine) — AI generator in C2PA metadata
- [C2PA Specification](https://c2pa.org/specifications/) — Content Authenticity standard
- [IPTC Digital Source Type vocabulary](https://cv.iptc.org/newscodes/digitalsourcetype/) — `trainedAlgorithmicMedia` definition
- Challenge #16 writeup — Same generator (Grok Imagine), same C2PA structure, no geolocation
- Challenge #17 writeup — Confirms "costanera" + Argentina thematic context

(End of file - total 94 lines)