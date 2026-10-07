#!/usr/bin/env python3
"""Deriva el nombre de carpeta canónico de un reto: 05-banco-capybara-acceso-interno.

Uso: curl .../api/v1/challenges/<id> | ctf_slug.py
"""
import json
import re
import sys
import unicodedata


def main() -> None:
    d = json.load(sys.stdin)["data"]
    s = unicodedata.normalize("NFKD", d["name"]).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    print(f"{int(d['id']):02d}-{s}")


if __name__ == "__main__":
    main()