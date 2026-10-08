#!/usr/bin/env python3
# solve.py — Challenge 17: El puente del paseo
# OSINT / Geolocation — Bridge identification from costanera photo
#
# This script extracts metadata from the challenge image and prints the
# evidence. The image has minimal EXIF (no GPS, no camera, no C2PA).
# Visual identification of the bridge is subjective; the earlier candidate
# EVIL{puente_colgante} was a hypothesis; the platform rejected it.
#
# Usage: python3 solve.py

import subprocess
import sys
from pathlib import Path

IMG_PATH = Path(__file__).parent / "puente.jpg"

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
    print("Challenge 17: El puente del paseo — Metadata Extraction")
    print("=" * 60)
    
    metadata = run_exiftool()
    print("\n[+] Full EXIFTOOL Output:")
    print(metadata)
    
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print("""
Image: 1200x1200 square, minimal EXIF (stripped)
- No GPS, no camera, no software tag, no C2PA
- Progressive JPEG, 72 DPI, Uncalibrated color space

VISUAL OBSERVATIONS (subjective, not forensic):
- Caption context: "Hermoso día en la costanera" (social media post)
- Visible: Waterfront promenade (costanera) + suspension bridge in background
- Bridge type: Two-pylon suspension bridge (cables, vertical suspenders)
- Geographic context: Argentina (CTF language, "costanera" terminology)

CANDIDATE EVALUATION:
1. Puente Colgante de Santa Fe (Puente Ingeniero Marcial Candioti)
   - Connects Costanera Oeste ↔ Costanera Este across Laguna Setúbal
   - Iconic suspension bridge on Santa Fe's costanera
   - Flag format "puente_xxxxxx_xxxxxxxx" → "puente_colgante" fits pattern
   - Challenge #16 thematic correlation: Santa Fe (but #16 also rejected)
   - Official sources confirm "costanera" + "puente colgante" phrasing

2. Other Argentine bridges considered and not matching:
   - Puente de la Mujer (Buenos Aires): cable-stayed, single pylon, in dique
   - Puente Alsina/Pueyrredón (Buenos Aires): truss/bascule/box-girder
   - Zárate-Brazo Largo / Rosario-Victoria: cable-stayed, highway, intercity
   - None match "costanera" + two-pylon suspension bridge in urban setting

EARLIER CANDIDATE (REJECTED):
- EVIL{puente_colgante} — visual hypothesis + thematic correlation
- Platform verdict: INCORRECT

CONCLUSION:
No confirmed answer. The artifact provides no geolocation metadata.
Visual bridge matching is not verifiable. Flag remains unknown.
""")
    
    print("\n[+] Status: No confirmed flag — platform rejected visual hypothesis.")
    return 0

if __name__ == "__main__":
    sys.exit(main())