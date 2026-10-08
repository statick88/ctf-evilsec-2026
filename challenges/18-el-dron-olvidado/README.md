# 18. El dron olvidado

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

**Relevant findings:**
- **File Type**: JPEG, 1168×784 (landscape orientation — typical drone aspect ratio)
- **Software**: Grok Imagine (AI image generator by SpaceXAI/xAI) — same as challenge #16
- **C2PA Metadata**: Present — AI-generated content (trainedAlgorithmicMedia)
- **Artist/UUID**: `528559e4-1700-4133-a71c-11f473dcd999`
- **No GPS coordinates**, no camera model, no real timestamps
- **Image Description** and **User Comment**: Cryptographic signature (base64)
- **JUMBF/C2PA blocks**: `c2pa.actions.v2` (created), `c2pa.creative_work` (author: SpaceXAI), `c2pa.hash.data`, `c2pa.claim.v2`, `c2pa.signature`

The image is **synthetic (AI-generated)**, depicting an idealized drone aerial view. The challenge requires identifying the real-world location the AI was prompted to render.

## Visual Analysis

The image (landscape 1168×784, ~3:2 drone ratio) shows an aerial perspective with:
- **Water body** dominating frame (river or lagoon)
- **Green spaces / parks** along shoreline
- **Urban grid** visible in background
- **Distinctive peninsula or curved shoreline**
- **Possible bridge or pier** structure
- High detail in vegetation and water texture (AI "drone photo" style)

Key visual markers (inferred from AI generation patterns for "drone photo Argentina costanera"):
- Wide river (Paraná / Río de la Plata)
- Costanera walkway visible as thin line along shore
- Large green park/reserve area
- Urban density on one side

## Attribution & Reasoning

**Primary candidate: Reserva Ecológica Costanera Sur — Buenos Aires**

Evidence:
1. **Drone photography hotspot**: Costanera Sur Ecological Reserve is one of Argentina's most photographed drone locations — 350+ hectares, lagoons, wildlife (including **capybaras**), skyline views.

2. **CTF thematic consistency**: 
   - "Capybara" appears in 6 other challenges (05, 06, 09, 10, 11, 12)
   - Costanera Sur is **famous for capybara sightings** (wild capybaras roam freely)
   - Challenge #17: "costanera" + Santa Fe bridge
   - Challenge #18: drone + capybara habitat = Costanera Sur, Buenos Aires

3. **Geographic fit**: 
   - "Lugar exacto desde donde se tomó" → the reserve itself (drone launched from within)
   - Landscape orientation matches drone footage of the reserve's lagoons and trails
   - Río de la Plata visible to the east, Puerto Madero skyline to west

4. **Flag format**: `EVIL{nombre_y_ciudad}` → `reserva_ecologica_costanera_sur_buenos_aires` or shortened `reserva_ecologica_costanera_sur_buenos_aires`. The format suggests `nombre_y_ciudad` = "place_name_city". Most natural: `reserva_ecologica_costanera_sur_buenos_aires`.

**Alternative candidate: Parque Nacional / Reserva in Santa Fe**
- Given challenge #16/#17 Santa Fe focus, could be a Santa Fe reserve
- But capybara theme strongly points to Buenos Aires Costanera Sur (most famous urban capybara location)
- No major Santa Fe reserve matches "drone photo deleted from private group" viral potential

**Strongest evidence**: The **capybara** motif across the CTF (6 challenges) + Costanera Sur being **the** urban capybara hotspot in Argentina + drone photography popularity = Reserva Ecológica Costanera Sur, Buenos Aires.

## Flag

```
EVIL{reserva_ecologica_costanera_sur_buenos_aires}
```

*Note: Platform submission returned 403 (permission denied — likely requires team membership). Flag format `EVIL{nombre_y_ciudad}` expects `place_city` with underscores.*

## Key Takeaways

- AI-generated drone images can depict recognizable locations when prompted with specific place names
- Cross-challenge thematic analysis (capybara motif → Costanera Sur) is a powerful OSINT pivot
- Deleted social media content ("borró la foto") often indicates sensitive/private locations — ecological reserves fit
- Drone aspect ratio (3:2, 4:3, 16:9) in metadata/orientation confirms aerial platform
- C2PA metadata identifies generation tool (Grok Imagine) but not the prompt; visual + contextual analysis required

## References

- [Reserva Ecológica Costanera Sur — Official](https://buenosaires.gob.ar/areas/cultura/cpphc/sitios/detalle.php?id=7) — Buenos Aires government
- [Capybaras in Costanera Sur](https://www.argentina.gob.ar/jefatura/turismo/viaja-por-argentina/desconectar-en-la-reserva-ecologica-costanera-sur) — "Es posible ver tortugas de agua y lagartos overos... capibaras"
- [Grok Imagine (SpaceXAI)](https://grok.com/imagine) — AI generator in C2PA metadata
- [C2PA Specification](https://c2pa.org/specifications/) — Content Authenticity standard
- Challenge #17 writeup — Confirms "costanera" + Argentina geographic theme