#!/usr/bin/env python3
"""Lista los retos ya resueltos por la sesión actual.

Uso: curl .../api/v1/challenges | solved.py
"""
import json
import sys


def main() -> None:
    data = sorted(json.load(sys.stdin)["data"], key=lambda c: c["id"])
    solved = [c for c in data if c["solved_by_me"]]
    if not solved:
        print("(ninguno todavía)")
        return
    for c in solved:
        print(f"{c['id']}\t{c['value']}p\t{c['name']}")
    print(f"\n{len(solved)}/{len(data)} retos · {sum(c['value'] for c in solved)} puntos")


if __name__ == "__main__":
    main()