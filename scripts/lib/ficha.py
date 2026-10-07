#!/usr/bin/env python3
"""Genera challenges/<slug>/FICHA.md a partir de metadata.json (sin tokens)."""
import html
import json
import re
import sys
from pathlib import Path

CAT_ES = {
    "WEB": "Web",
    "REVERSING": "Reversing",
    "FORENSIC": "Forense",
    "OSINT": "OSINT",
    "MISC": "Misc",
}


def clean(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def main() -> None:
    root = Path(sys.argv[1])
    for meta in sorted(root.glob("challenges/*/metadata.json")):
        d = json.load(meta.open())["data"]
        out = meta.parent / "FICHA.md"
        urls = re.findall(r"https?://[^\s<>\"')]+", clean(d["description"]))
        lines = [
            f"# {d['id']}. {d['name']}",
            "",
            f"- **Categoría**: {CAT_ES.get(d['category'], d['category'])} (`{d['category']}`)",
            f"- **Puntos**: {d['value']}",
            f"- **Dificultad**: {', '.join(d['tags']) or 'n/d'}",
            f"- **Resoluciones**: {d['solves']}",
            "",
            "## Enunciado",
            "",
            clean(d["description"]),
        ]
        if urls:
            lines += ["", "## Objetivos remotos", ""] + [f"- {u}" for u in urls]
        if d.get("files"):
            lines += ["", "## Artefactos", ""] + [
                f"- `{Path(f.split('?')[0]).name}`" for f in d["files"]
            ]
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[ok] {out.relative_to(root)}")


if __name__ == "__main__":
    main()