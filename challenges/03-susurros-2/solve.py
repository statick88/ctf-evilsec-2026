#!/usr/bin/env python3
# solve.py — Susurros 2 (HARD)
# Streaming extraction of unique anomaly lines from server.log, decoding fragments,
# and reconstructing the candidate flag in timestamp order.
#
# Fragments found (in timestamp order):
# 1. INFO audit ascii_dec=69.86.73.76 -> "EVIL"
# 2. DEBUG heartbeat crc32=ezNsXw== (base64) -> "{3l_" -> leetspeak 3=e -> "{el_"
# 3. INFO etl_job stage=62 blob=c3VzdQ== (base64) -> "susu"
# 4. INFO etl_job stage=32 blob=ee0_ (plain) -> rot13 -> "rr0_" -> leetspeak 0=o -> "rro_"
# 5. INFO etl_job stage=40 blob=30736375 (hex) -> "0scu" -> leetspeak 0=o -> "oscu"
# 6. INFO etl_job stage=47 blob=98.51.57.125 (ASCII decimal IP) -> "b39}"
#
# Candidate flag: EVIL{el_susurro_oscub39}  (reads as "el susurro oscuro b39")
# Platform verdict: INCORRECT — fragment 6 (b39}) contradicts linguistic completion (ro}).
# This script prints the candidate for analysis. The flag is NOT confirmed by the platform.

import sys
import base64
import re

def rot13(s: str) -> str:
    return s.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
    ))

def leet(s: str) -> str:
    return s.translate(str.maketrans({"3": "e", "0": "o", "4": "a", "1": "i"}))

def decode_ascii_dec(s: str) -> str:
    """Decode dot-separated decimal ASCII codes."""
    return ''.join(chr(int(x)) for x in s.split('.'))

def main():
    log_file = "server.log"
    
    # Patterns for the 6 unique real lines (non-decoy)
    patterns = [
        # (regex, decoder_func, description)
        (r'INFO audit user=svc_backup ascii_dec=([\d.]+)', 
         lambda m: decode_ascii_dec(m.group(1)), 
         "audit ascii_dec -> EVIL"),
        (r'DEBUG heartbeat crc32=([A-Za-z0-9+/=]+)',
         lambda m: leet(base64.b64decode(m.group(1)).decode()),
         "heartbeat crc32 base64 -> {el_"),
        (r'INFO etl_job stage=62 blob=([A-Za-z0-9+/=]+)',
         lambda m: base64.b64decode(m.group(1)).decode(),
         "etl_job stage62 base64 -> susu"),
        (r'INFO etl_job stage=32 blob=([^ ]+)',
         lambda m: leet(rot13(m.group(1))),
         "etl_job stage32 plain -> rot13+leet -> rro_"),
        (r'INFO etl_job stage=40 blob=([0-9a-fA-F]+)',
         lambda m: leet(bytes.fromhex(m.group(1)).decode()),
         "etl_job stage40 hex -> leet -> oscu"),
        (r'INFO etl_job stage=47 blob=([\d.]+)',
         lambda m: decode_ascii_dec(m.group(1)),
         "etl_job stage47 ASCII decimal IP -> b39}"),
    ]
    
    # Compile all patterns
    compiled = [(re.compile(p), fn, desc) for p, fn, desc in patterns]
    
    # Track found fragments in timestamp order (file is already timestamp-sorted)
    fragments = []
    found_patterns = set()
    
    with open(log_file, 'r') as f:
        for line in f:
            for i, (regex, decoder, desc) in enumerate(compiled):
                if i in found_patterns:
                    continue
                m = regex.search(line)
                if m:
                    try:
                        fragment = decoder(m)
                        fragments.append(fragment)
                        found_patterns.add(i)
                    except Exception as e:
                        print(f"Decode error for {desc}: {e}", file=sys.stderr)
    
    # Assemble candidate flag
    candidate = ''.join(fragments)
    print(f"Candidate flag (NOT confirmed by platform): {candidate}")
    print("Note: Fragment 6 yields 'b39}' but linguistic completion expects 'ro}'.")
    print("Platform verdict for this candidate: INCORRECT")

if __name__ == "__main__":
    main()