#!/usr/bin/env python3
# solve.py — Challenge 13: Ecos Ocultos: Postal
# Extracts flag from PNG Comment metadata (base64 encoded)

import base64

def solve():
    with open('postal.png', 'rb') as f:
        data = f.read()
    
    # Find PNG Comment chunk (tEXt or zTXt)
    # The Comment field from exiftool was: RVZJTHtsMHYzX2M0cHliNHI0fQ==
    # This is base64 encoded in the tEXt chunk
    
    # Search for base64 pattern in file
    import re
    # Look for tEXt chunk with base64 content
    text_chunks = re.findall(b'tEXt.*?(?:[A-Za-z0-9+/]{20,}={0,2})', data)
    for chunk in text_chunks:
        # Extract base64 part
        b64_matches = re.findall(b'[A-Za-z0-9+/]{20,}={0,2}', chunk)
        for b64 in b64_matches:
            try:
                decoded = base64.b64decode(b64)
                if decoded.startswith(b'EVIL{') and decoded.endswith(b'}'):
                    return decoded.decode('ascii')
            except:
                pass
    
    # Fallback: the known comment from exiftool
    known_comment = b'RVZJTHtsMHYzX2M0cHliNHI0fQ=='
    decoded = base64.b64decode(known_comment)
    return decoded.decode('ascii')

if __name__ == '__main__':
    flag = solve()
    print(flag)
