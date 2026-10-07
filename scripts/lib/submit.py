#!/usr/bin/env python3
"""Interpreta la respuesta del endpoint de submission de la plataforma.

Uso: ctf ... | submit.py
"""
import json
import sys


def main() -> None:
    r = json.load(sys.stdin)
    d = r.get("data") or {}
    status = d.get("status") or r.get("status") or r.get("message") or "?"
    print(f"VEREDICTO: {status}")
    if d.get("message"):
        print(f"mensaje: {d['message']}")
    for key in ("value", "solves", "attempt"):
        if key in d:
            print(f"{key}: {d[key]}")


if __name__ == "__main__":
    main()