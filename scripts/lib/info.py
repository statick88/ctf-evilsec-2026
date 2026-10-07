#!/usr/bin/env python3
"""Imprime la ficha de un reto: metadatos, descripción, pistas y ficheros.

Uso: curl .../api/v1/challenges/<id> | ctf_info.py
"""
import html
import json
import re
import sys


def clean(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def main() -> None:
    d = json.load(sys.stdin)["data"]
    print(f"# {d['id']} {d['name']}")
    print(
        f"categoria={d['category']}  puntos={d['value']}  "
        f"tags={d['tags']}  solves={d['solves']}"
    )
    print()
    print(clean(d["description"]))
    hints = d.get("hints") or []
    if hints:
        print("\nPISTAS:")
        for i, h in enumerate(hints, 1):
            print(f"  {i}. {clean(h) if isinstance(h, str) else h}")
    files = d.get("files") or []
    if files:
        print("\nARCHIVOS:")
        for f in files:
            print(f"  {f}")
    print("\nRUTAS:")
    for url in re.findall(r"https?://[^\s<>\"')]+", clean(d["description"])):
        print(f"  {url}")


if __name__ == "__main__":
    main()