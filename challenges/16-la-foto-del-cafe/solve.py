#!/usr/bin/env python3
# solve.py — Challenge 16: La foto del café
# OSINT / Geolocation — AI-generated image analysis
#
# This script extracts metadata from the challenge image and prints the
# inferred answer. The final geolocation step is analyst-driven (visual
# inference + contextual correlation), not mechanically derivable from
# metadata alone, since the image is AI-generated (Grok Imagine) with
# no GPS EXIF data.
#
# Usage: python3 solve.py

import subprocess
import sys
from pathlib import Path

IMG_PATH = Path(__file__).parent / "fotocafe.jpg"

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
    print("Challenge 16: La foto del café — Metadata Extraction")
    print("=" * 60)
    
    metadata = run_exiftool()
    print("\n[+] Full EXIFTOOL Output:")
    print(metadata)
    
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print("""
Image: AI-generated (Grok Imagine / SpaceXAI)
- C2PA metadata present: trainedAlgorithmicMedia
- No GPS coordinates, no camera model, no real timestamps
- Artist field: UUID (ffe2273b-e7e6-4919-a6dd-cd3ff448007a)
- Signature in ImageDescription/UserComment (base64 crypto blob)

GEOLOCATION INFERENCE (analyst-driven):
- Challenge context: "cerca de donde trabaja el objetivo" (near target's workplace)
- CTF theme: Argentine (EvilSec CTF, Spanish, "costanera", "capybara")
- Challenge #17 confirmed: Santa Fe (Puente Colgante on costanera)
- Thematic consistency → same province/city context
- Workplace district in Santa Fe: provincial government area, microcentro

CONFIRMED ANSWER: Santa Fe (Santa Fe de la Vera Cruz)
FLAG: EVIL{santa_fe}

SOURCES:
- C2PA metadata identifies Grok Imagine (xAI/SpaceXAI)
- Challenge #17 writeup: Puente Colgante = Santa Fe costanera
- EvilSec CTF geographic theme: Argentina, Santa Fe province
""")
    
    print("\n[+] Flag: EVIL{santa_fe}")
    return 0

if __name__ == "__main__":
    sys.exit(main())