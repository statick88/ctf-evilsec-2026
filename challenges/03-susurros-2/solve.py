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
# 7. INFO audit token_hex=4556494c7b6e305f7330797d (hex) -> "EVIL{n0_s0y}"
#    ("no_soy" = "I'm not [it]": TRAP in the trusted audit source, byte-identical
#    in meaning to the dns payload_b64 decoy; submitted, INCORRECT)
#
# Candidate flag: EVIL{el_susurro_oscub39}  (reads as "el susurro oscuro b39")
# Platform verdict: INCORRECT — and so is every other candidate in the closed
# mechanical space (see CANDIDATE VERDICTS below and README.md).
#
# FRAGMENT-6 EXHAUSTIVENESS (all verified in-session against the platform):
# - Closed anomaly census (digit/hex-normalized templates, full 120k-line sweep):
#   exactly 13 rare templates (heartbeatx1, auditx2, etl_jobx4, authx2, dnsx4)
#   plus 2 FLAGPART templates (9x {FAKE_0xXX}, 9x ??NNN?? corrupted). No 8th fragment.
# - Single-key proof: for octets [98,51,57,125], any single-byte XOR / modular-add /
#   Caesar key k with (125+k)==125 forces k==identity, so no single-key cipher can
#   yield a different '}'-terminated tail. Whole family dead in one stroke.
# - Mirror ("}93b") and ROT47 ("3bhN") destroy the closing brace: invalid tails.
# - ROT13 ("o39}"), Caesar-16 ("r39}"), atbash ("y39}"), leet 3->e ("be9}"),
#   rot13+leet ("oe9}"), mirror-segment ("93b}"), 9->g ("beg}"), Caesar+3 ("e39}"):
#   all submitted (R1 middle) -> INCORRECT.
# - Leet on/off per block (F2/F4/F5): all 8 middles x "b39}" submitted -> INCORRECT.
# - Linguistic completions ("oscuro", "oscuro_b39", "oscuro39", "oscurob39",
#   "oscur0", "oscuro_") and standalone decoys ("n0_s30y","f4ls0_","d3c0y!","n0_s0y")
#   submitted -> INCORRECT.
# - heartbeat "crc32" value is NOT a checksum of any flag/part/block (59-way brute
#   force against 0x7b336c5f, incl. all block-substrings): field is flavor text.
# - rows=/stage=/shard= values are singletons with no linked records; octet/row/
#   stage numbers as log-line pointers hit generic noise lines.
#
# CANDIDATE VERDICTS (platform /api/v1/challenges/attempt, all "incorrect"):
#   EVIL{el_susurro_oscub39}  (R1 raw; history + reconfirmed in-session)
#   EVIL{3l_susurr0_0scub39}  (R2, no leet anywhere)
#   EVIL{el_susurr0_0scub39}, EVIL{3l_susurro_oscub39}, EVIL{el_susurr0_oscub39},
#   EVIL{el_susurro_0scub39}, EVIL{3l_susurr0_oscub39}, EVIL{3l_susurro_0scub39}
#   (all 6 mixed leet middles x b39 tail)
#   EVIL{el_susurro_oscuro}, EVIL{3l_susurr0_0scur0}, EVIL{el_susurro_oscuro_b39},
#   EVIL{el_susurro_oscuro39}, EVIL{el_susurro_oscurob39}, EVIL{el_susurro_oscur0},
#   EVIL{el_susurro_oscuro_}  (linguistic completions)
#   EVIL{el_susurro_oscube9}, EVIL{el_susurro_oscuoe9}, EVIL{el_susurro_oscuo39},
#   EVIL{el_susurro_oscur39}, EVIL{el_susurro_oscue39}, EVIL{el_susurro_oscu93b},
#   EVIL{el_susurro_oscubeg}  (frag-6 post-transforms)
#   EVIL{n0_s0y}, EVIL{f4ls0_}, EVIL{d3c0y!}  (standalone full-flags; the audit
#   trap decodes to n0_s0y, identical to the dns b64 decoy)
#   EVIL{EL_SUSURRO_OSCUB39}  (case variant)
#
# This script prints the R1 candidate for analysis. The flag is NOT confirmed by
# the platform. DO NOT create flag.txt from unconfirmed output.

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
        (r'INFO audit user=svc_backup token_hex=([0-9a-fA-F]+)',
         lambda m: bytes.fromhex(m.group(1)).decode(),
         "audit token_hex TRAP -> EVIL{n0_s0y} (dup of dns decoy; INCORRECT)"),
    ]
    
    # Compile all patterns
    compiled = [(re.compile(p), fn, desc) for p, fn, desc in patterns]
    
    # Track found fragments in timestamp order (file is already timestamp-sorted),
    # keyed by pattern index so the audit trap (pattern 6) can be excluded.
    found = {}

    with open(log_file, 'r') as f:
        for line in f:
            for i, (regex, decoder, desc) in enumerate(compiled):
                if i in found:
                    continue
                m = regex.search(line)
                if m:
                    try:
                        found[i] = decoder(m)
                    except Exception as e:
                        print(f"Decode error for {desc}: {e}", file=sys.stderr)

    # Assemble candidate flag from the 6 chain fragments (patterns 0-5);
    # pattern 6 is the documented audit trap.
    chain = [found[i] for i in range(6) if i in found]
    candidate = ''.join(chain)
    print(f"Candidate flag (NOT confirmed by platform): {candidate}")
    print("Note: Fragment 6 yields 'b39}' but linguistic completion expects 'ro}'.")
    print("Platform verdict for this candidate AND all 30 sibling variants: INCORRECT")
    if 6 in found:
        print(f"Audit trap line decodes to: {found[6]} (submitted standalone: INCORRECT)")
    print("See README.md for the closed anomaly census and full verdict table.")

if __name__ == "__main__":
    main()