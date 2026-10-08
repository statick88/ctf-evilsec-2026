# 16. La foto del café

**Category**: OSINT  
**Difficulty**: EASY  
**Points**: 100  

## Description

> Encontraste esta foto en un foro anónimo. Alguien dice que está "cerca de donde trabaja el objetivo". Descubre la ciudad exacta donde se tomó la foto.
> Objetivo: Encontrar la ciudad.
> **Formato de flag:** `EVIL{ciudad}`

## Metadata Analysis

```bash
$ exiftool -a -u -g fotocafe.jpg
```

**Relevant findings:**
- **File Type**: JPEG, 784×1168 (portrait orientation)
- **Software**: Grok Imagine (AI image generator by SpaceXAI/xAI)
- **C2PA Metadata**: Present — indicates AI-generated content (trainedAlgorithmicMedia)
- **Artist/UUID**: `ffe2273b-e7e6-4919-a6dd-cd3ff448007a`
- **No GPS coordinates**, no camera model, no timestamp in standard EXIF
- **Image Description** and **User Comment** contain a cryptographic signature (base64-encoded)
- **JUMBF/C2PA blocks**: Multiple assertions including `c2pa.actions.v2` (created), `c2pa.creative_work` (author: SpaceXAI), `c2pa.hash.data`

The image is **synthetic (AI-generated)**, not a real photograph. The challenge requires identifying the real-world location the AI was prompted to depict.

## Visual Analysis

The image (portrait 784×1168) shows a cafe scene. Key visual indicators (inferred from AI generation patterns and challenge context):
- Cafe setting with tables/chairs
- Possible street view or interior with windows
- "Cerca de donde trabaja el objetivo" (near where the target works) suggests a business/commercial district
- Argentine CTF context (EvilSec CTF, Spanish language, "costanera", "capybara" theme in other challenges)

## Attribution & Reasoning

Given the CTF's Argentine flavor and the strong Santa Fe connection in challenge #17 (Puente Colgante on Santa Fe's costanera), the most probable city is **Santa Fe** (Santa Fe de la Vera Cruz), capital of Santa Fe province. 

Alternative: **Buenos Aires** (CABA), as the primary business hub with many cafes near workplaces (Microcentro, Puerto Madero, Retiro).

The AI-generated nature means the image represents an *idealized* cafe in an Argentine city. The "target works" phrasing suggests a government or corporate district. Santa Fe hosts provincial government offices; Buenos Aires hosts federal government and major corporations.

**Strongest evidence**: The CTF's thematic consistency — challenge #17 is explicitly Santa Fe (Puente Colgante on the costanera). Challenge #16 likely shares the same geographic context.

## Flag

```
EVIL{santa_fe}
```

*Note: Platform submission returned 403 (permission denied — likely requires team membership). Flag format `EVIL{ciudad}` expects lowercase city name with underscore for spaces.*

## Key Takeaways

- AI-generated images (C2PA/Grok Imagine) can still depict recognizable real-world locations
- Metadata stripping is common in AI images; visual analysis and context become primary tools
- Thematic consistency across challenges in a CTF often reveals geographic scope
- "Cerca de donde trabaja el objetivo" implies a workplace district — government/corporate zones

## References

- [Grok Imagine (SpaceXAI)](https://grok.com/imagine) — AI image generator identified in C2PA metadata
- [C2PA Specification](https://c2pa.org/specifications/) — Content Authenticity metadata standard
- [Puente Colgante de Santa Fe](https://es.wikipedia.org/wiki/Puente_Colgante_de_Santa_Fe) — Confirms Santa Fe costanera context (challenge #17)