#!/usr/bin/env python3
"""Formatea la lista de retos del evento como tabla legible.

Uso: curl .../api/v1/challenges | ctf_list.py
"""
import json
import sys


def main() -> None:
    data = json.load(sys.stdin)["data"]
    data.sort(key=lambda c: c["id"])
    print(f"{'ID':>3}  {'CATEGORIA':<10} {'PTS':>4}  {'TAG':<7} {'OK':<3} NOMBRE")
    total = 0
    for c in data:
        tags = ",".join(t["value"] for t in c["tags"])
        ok = " SI" if c["solved_by_me"] else ""
        mark = " *" if c["solved_by_me"] else ""
        total += c["value"]
        print(f"{c['id']:>3}  {c['category']:<10} {c['value']:>4}  {tags:<7}{ok:<3} {c['name']}{mark}")
    print(f"\n{len(data)} retos · {total} puntos en juego")


if __name__ == "__main__":
    main()