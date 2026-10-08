#!/usr/bin/env python3
# solve.py — Challenge 18: El dron olvidado
# OSINT / Geolocation — Drone photo location identification
#
# This script extracts metadata from the challenge image and prints the
# evidence. The image is AI-generated (Grok Imagine) with no GPS EXIF data.
# No geolocation can be derived from the artifact. The earlier candidate
# EVIL{reserva_ecologica_costanera_sur_buenos_aires} was a thematic hypothesis;
# the platform rejected it.
#
# Usage: python3 solve.py

import subprocess
import sys
from pathlib import Path

IMG_PATH = Path(__file__).parent / "dron.jpg"

def run_exiftool():
    """Extract all metadata using exiftool."""
    try:
        result = subprocess.run(
            ["exiftool", "-a", "-u", "-g", str(IMG_PATH)],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout
    except FileNotFoundError:
        return "exiftool not installed"
    except subprocess.TimeoutExpired:
        return "exiftool timeout"

def main():
    print("=" * 60)
    print("Challenge 18: El dron olvidado — Metadata Extraction")
    print("=" * 60)
    
    metadata = run_exiftool()
    print("\n[+] Full EXIFTOOL Output:")
    print(metadata)
    
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print("""
Image: AI-generated (Grok Imagine / SpaceXAI) — same generator as Challenge #16
- C2PA metadata: trainedAlgorithmicMedia
- Software Agent: Grok Imagine
- Author: SpaceXAI (Organization)
- Artist UUID: 528559e4-1700-4133-a71c-11f473dcd999 (different from #16)
- No GPS, no camera, no real timestamps, no location assertions
- Landscape 1168x784 (~3:2) — typical drone photo aspect ratio (prompted format)

VISUAL OBSERVATIONS (subjective, not forensic):
- Perspective: Aerial, water + green space + urban grid
- "Drone photo deleted from private group" — narrative framing
- CTF theme: "Capybara" appears in 6 challenges (05,06,09,10,11,12)
- Challenge #17: "costanera" + Argentina context
- Geographic context: Argentina (language, themes)

CANDIDATE EVALUATION:
1. Reserva Ecológica Costanera Sur — Buenos Aires
   - #1 drone photography spot in Argentina (350 ha, lagoons, skyline)
   - Known for wild capybaras (CTF mascot theme)
   - "Costanera" term matches challenge #17 terminology
   - BUT: Image shows no identifiable landmarks of the reserve
   - No specific lagoon shapes, no Puerto Madero skyline, no trail network

2. Santa Fe reserves / costaneras
   - Challenge #16/#17 suggest Santa Fe focus (but both rejected)
   - No Santa Fe reserve matches capybara fame + drone virality

3. Generic AI "drone photo costanera" synthesis
   - Grok Imagine generates plausible but non-specific scenes
   - Water + green + urban grid = generic costanera archetype
   - No prompt location name recoverable from output

EARLIER CANDIDATE (REJECTED):
- EVIL{reserva_ecologica_costanera_sur_buenos_aires}
- Basis: Thematic correlation (capybara motif + costanera + drone ratio)
- Platform verdict: INCORRECT

CONCLUSION:
No confirmed answer. The artifact is synthetic with no geolocation metadata.
Thematic hypotheses are not verifiable. Flag remains unknown.
""")
    
    print("\n[+] Status: No confirmed flag — platform rejected thematic hypothesis.")
    return 0

if __name__ == "__main__":
    sys.exit(main())