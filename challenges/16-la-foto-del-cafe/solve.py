#!/usr/bin/env python3
# solve.py — Challenge 16: La foto del café
# OSINT / Geolocation — AI-generated image metadata extraction
#
# This script extracts metadata from the challenge image and prints the
# evidence. The image is AI-generated (Grok Imagine) with no GPS EXIF data.
# No geolocation can be derived from the artifact. The earlier candidate
# EVIL{santa_fe} was a thematic hypothesis; the platform rejected it.
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
- Software Agent: Grok Imagine
- Author: SpaceXAI (Organization)
- No GPS coordinates, no camera model, no real timestamps
- Artist field: UUID (ffe2273b-e7e6-4919-a6dd-cd3ff448007a)
- Signature in ImageDescription/UserComment (base64 crypto blob)
- Image dimensions: 784x1168 (portrait)

GEOLOCATION ASSESSMENT:
- The image is synthetic; visual analysis cannot identify a real location
- No EXIF GPS, no XMP GPS, no C2PA location assertions
- Challenge narrative ("cerca de donde trabaja el objetivo") is a story element
- CTF thematic context (Argentina, Santa Fe in #17) is not evidence

EARLIER CANDIDATE (REJECTED):
- EVIL{santa_fe} — based on thematic correlation with challenge #17
- Platform verdict: INCORRECT

CONCLUSION:
No confirmed answer. The artifact contains no geolocation data.
Flag remains unknown.
""")
    
    print("\n[+] Status: No confirmed flag — platform rejected thematic candidate.")
    return 0

if __name__ == "__main__":
    sys.exit(main())