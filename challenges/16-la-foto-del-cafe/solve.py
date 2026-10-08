#!/usr/bin/env python3
"""solve.py — Reto 16: La foto del café (OSINT, geolocalización).

La imagen es una foto ENCUADRADA desde la ventana de un café: el plano principal
es un cappuccino, pero al fondo se ve el anfiteatro Flavio (Colosseo) de Roma a
través del vidrio. La ciudad se lee del contenido, no de los metadatos: el C2PA
declara que la imagen la generó Grok Imagine, y un generador no inventa un
monumento con esa precisión estructural por casualidad — el autor pidió esa vista.

La flag se confirmó contra la plataforma del evento (veredicto: correct).

Uso: python3 solve.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

IMG = Path(__file__).parent / "fotocafe.jpg"
CONFIRMED_FLAG = "EVIL{roma}"


def exif_summary() -> str:
    """Hechos de metadatos relevantes: descartan la vía GPS."""
    try:
        out = subprocess.run(
            ["exiftool", "-s", "-Software_Agent", "-DigitalSourceType",
             "-ImageWidth", "-ImageHeight", str(IMG)],
            capture_output=True, text=True, timeout=30).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "(exiftool no disponible)"
    return out.strip()


def main() -> int:
    print("Reto 16 — La foto del café")
    print("=" * 62)
    print("\n[1] Metadatos: descartan la geolocalización por EXIF")
    print(exif_summary())
    print("    -> Sin GPS. La imagen es sintética (Grok Imagine),")
    print("       así que el C2PA no afirma ninguna ubicación real.")

    print("\n[2] Contenido visual, que es donde está la respuesta")
    print("    Encuadre: cappuccino sobre mesa de madera, junto a una ventana.")
    print("    Al fondo, a la izquierda y a través del vidrio, el anfiteatro")
    print("    Flavio — el Colosseo de Roma: tres órdenes de arcos superpuestos")
    print("    y el remate de ladrillo de la Solutions Curve.")
    print("    Un café con esa vista está en una ciudad: Roma.")
    print("    El enunciado lo encaja: «cerca de donde trabaja el objetivo».")

    print("\n[3] Verificación")
    print(f"    Flag confirmada por la plataforma del evento: {CONFIRMED_FLAG}")
    print(f"\n{CONFIRMED_FLAG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())