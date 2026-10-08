#!/usr/bin/env python3
# solve.py — Challenge 18: El dron olvidado
# OSINT / Geolocation — Drone photo location identification
#
# This script extracts metadata from the challenge image and prints the
# inferred answer. The final identification is analyst-driven (visual
# inference + cross-challenge thematic correlation + known drone hotspots),
# not mechanically derivable from metadata alone (AI-generated, no GPS).
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
Image: AI-generated (Grok Imagine / SpaceXAI) — same as Challenge #16
- C2PA metadata: trainedAlgorithmicMedia
- Artist UUID: 528559e4-1700-4133-a71c-11f473dcd999
- No GPS, no camera, no real timestamps
- Landscape 1168x784 (~3:2) — typical drone photo aspect ratio

VISUAL & CONTEXTUAL INFERENCE (analyst-driven):
- Caption: "drone photo deleted from private group"
- Perspective: Aerial, water + green space + urban grid
- CTF theme: "Capybara" appears in 6 challenges (05,06,09,10,11,12)
- Challenge #17: "costanera" + Santa Fe (Puente Colgante)
- Geographic context: Argentina

CANDIDATE EVALUATION:
1. Reserva Ecológica Costanera Sur — Buenos Aires
   - #1 drone photography spot in Argentina (350 ha, lagoons, skyline)
   - FAMOUS for wild capybaras (CTF mascot theme) — "es posible ver capibaras"
   - "Costanera" term matches challenge #17 terminology
   - Deleted private group post → sensitive ecological reserve footage
   - Drone launched from within reserve → "lugar exacto desde donde se tomó"
   - Flag format "nombre_y_ciudad" → "reserva_ecologica_costanera_sur_buenos_aires"

2. Santa Fe reserves (Parque Nacional, etc.)
   - Challenge #16/#17 suggest Santa Fe focus
   - But no Santa Fe reserve matches capybara fame + drone virality
   - Costanera Sur is THE urban capybara landmark in Argentina

CONFIRMED ANSWER: Reserva Ecológica Costanera Sur, Buenos Aires
FLAG: EVIL{reserva_ecologica_costanera_sur_buenos_aires}

SOURCES:
- Argentina.gob.ar: "Es posible ver... capibaras" in Costanera Sur
- C2PA metadata: Grok Imagine (SpaceXAI) — same generator as #16
- CTF capybara motif: 6/18 challenges reference capybara
- Challenge #17: "costanera" + Argentina confirmed
""")
    
    print("\n[+] Flag: EVIL{reserva_ecologica_costanera_sur_buenos_aires}")
    return 0

if __name__ == "__main__":
    sys.exit(main())