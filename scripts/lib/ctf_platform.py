#!/usr/bin/env python3
"""Reconciliación autoritativa contra la plataforma del CTF.

Este módulo no confía en los writeups: la fuente de verdad es el endpoint de
submission y el scoreboard del evento. `flag.txt` por reto sólo puede existir si
la plataforma devolvió `correct`.

Subcomandos:
  audit      tabla de estado oficial (scoreboard + flag.txt + veredicto real)
  claim      somete una flag y, sólo si es `correct`, la registra como flag.txt
  readmes    lista writeups que afirman una flag sin flag.txt que la respalde
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Charset estricto: una flag real no lleva pipes, comillas, saltos de línea ni
# `%s`. Un regex laxo acaba extrayendo tablas de markdown o plantillas printf.
FLAG_RE = re.compile(r"EVIL\{[A-Za-z0-9_!$@#*.,+\-]{2,96}\}")
PLACEHOLDERS = {"ciudad", "nombre_y_ciudad", "s", "..."}


# ---------------------------------------------------------------- API client

class Platform:
    def __init__(self) -> None:
        self.base, self.session, self.csrf = self._load_env()
        self._refresh_csrf()

    def _load_env(self) -> tuple[str, str, str]:
        env: dict[str, str] = {}
        for line in (ROOT / ".env").read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
        import urllib.parse as up

        raw = env.get("url") or env.get("CTF_URL") or ""
        parts = up.urlsplit(raw)
        base = f"{parts.scheme}://{parts.netloc}" if parts.scheme else raw
        session = env.get("session") or env.get("CTF_SESSION") or ""
        if not base or not session:
            sys.exit("[!] .env debe definir url y session")
        return base, session, ""

    def _refresh_csrf(self) -> None:
        """El SPA de CTFd manda `CSRF-Token` en cada petición; sin él, los POST
        devuelven 403 con un mensaje que parece de permisos pero es CSRF."""
        html = self._get("/challenges")
        m = re.search(r"csrfNonce':\s*\"([a-f0-9]{16,})\"", html or "")
        self.csrf = m.group(1) if m else ""

    def _get(self, path: str) -> str:
        cmd = ["curl", "-sS", "-b", f"session={self.session}", f"{self.base}{path}"]
        return subprocess.run(cmd, capture_output=True, text=True).stdout

    def _post(self, path: str, payload: dict) -> dict:
        cmd = [
            "curl", "-sS", "-X", "POST",
            "-b", f"session={self.session}",
            "-H", f"CSRF-Token: {self.csrf}",
            "-H", "Accept: application/json",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
            f"{self.base}{path}",
        ]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return {"success": False, "data": {"status": f"respuesta no-JSON: {out[:80]!r}"}}

    # ------------------------------------------------------------- consultas

    def challenges(self) -> list[dict]:
        raw = self._get("/api/v1/challenges")
        data = json.loads(raw)["data"]
        return sorted(data, key=lambda c: c["id"])

    def submit(self, cid: int, flag: str) -> str:
        r = self._post("/api/v1/challenges/attempt",
                       {"challenge_id": cid, "submission": flag})
        d = r.get("data") or {}
        return d.get("status") or r.get("status") or "?"

    def me(self) -> dict:
        return json.loads(self._get("/api/v1/users/me"))["data"]


# ------------------------------------------------------------------ helpers

def slug_for(cid: int, name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return f"{cid:02d}-{s}"


def challenge_dirs() -> dict[str, Path]:
    out = {}
    for d in sorted((ROOT / "challenges").iterdir()):
        if d.is_dir():
            out[d.name.split("-", 1)[0]] = d
    return out


def readme_flag(dirpath: Path) -> str | None:
    """Flag afirmada por el writeup.

    Se prefiere la sección `## Flag` / `## Bandera`: es donde el autor declara la
    solución, no un ejemplo suelto dentro de la explicación. Si no existe esa
    sección se recurre al primer candidato no-placeholder del documento.
    """
    readme = dirpath / "README.md"
    if not readme.exists():
        return None
    text = readme.read_text()

    m = re.search(r"^##\s+(?:Flag|Bandera)\s*$", text, re.MULTILINE | re.IGNORECASE)
    scopes = []
    if m:
        rest = text[m.end():]
        nxt = re.search(r"^##\s+", rest, re.MULTILINE)
        flag_section = rest[: nxt.start()] if nxt else rest
        if re.search(r"no confirmed flag|sin flag confirmada", flag_section, re.IGNORECASE):
            return None
        scopes.append(flag_section)
    scopes.append(text)

    for scope in scopes:
        for cand in FLAG_RE.finditer(scope):
            val = cand.group(0)
            inner = val[5:-1]
            if inner in PLACEHOLDERS or set(inner) <= {"_", "."}:
                continue
            if inner.startswith("puente_xxxxxx"):
                continue
            return val
    return None


def stored_flag(dirpath: Path) -> str | None:
    f = dirpath / "flag.txt"
    return f.read_text().strip() if f.exists() else None


# --------------------------------------------------------------- subcomandos

def cmd_audit(plat: Platform) -> int:
    chals = plat.challenges()
    dirs = challenge_dirs()
    me = plat.me()

    print(f"Cuenta: {me['name']}  ·  puntos: {me['score']}  ·  team_id: {me['team_id']}")
    print(f"CSRF cargado: {'si' if plat.csrf else 'NO (los POST fallaran)'}\n")
    hdr = f"{'#':>3}  {'PTS':>4}  {'PLATAFORMA':<12} {'REPO':<10} {'FLAG REGISTRADA'}"
    print(hdr)
    print("-" * len(hdr))

    solved_official = 0
    total_pts = 0
    problems: list[str] = []

    for c in chals:
        cid = c["id"]
        d = dirs.get(f"{cid:02d}", ROOT / "challenges" / slug_for(cid, c["name"]))
        official = c["solved_by_me"]
        stored = stored_flag(d) if d.exists() else None
        claimed = readme_flag(d) if d.exists() else None

        solved_official += bool(official)
        total_pts += c["value"] if official else 0

        repo_state = "sin flag.txt"
        if stored:
            v = plat.submit(cid, stored)
            repo_state = "correct" if v in {"correct", "already_solved"} else f"RECHAZA({v})"
            if v not in {"correct", "already_solved"}:
                problems.append(
                    f"#{cid}: flag.txt={stored} rechazado por la plataforma ({v})")
        elif claimed:
            repo_state = "README≠∅"
            problems.append(
                f"#{cid}: el README afirma {claimed} pero no hay flag.txt respaldado")
        else:
            repo_state = "—"

        flagcol = stored if stored else (f"(README: {claimed})" if claimed else "—")
        print(f"{cid:>3}  {c['value']:>4}  "
              f"{'RESUELTO' if official else 'pendiente':<12} {repo_state:<10} {flagcol}")

    print(f"\nOficial: {solved_official}/{len(chals)} resueltos · {total_pts} puntos")
    if problems:
        print("\nINCOHERENCIAS repo <-> plataforma:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("Repo coherente con la plataforma.")
    return 0


def cmd_claim(plat: Platform, cid: int, flag: str) -> int:
    v = plat.submit(cid, flag)
    ok = v in {"correct", "already_solved"}
    print(f"#{cid} {flag} -> {v}")
    if not ok:
        print("NO se registra: la plataforma no lo confirmó.")
        return 1
    chals = {c["id"]: c for c in plat.challenges()}
    if cid not in chals:
        sys.exit(f"#{cid} no existe")
    d = ROOT / "challenges" / slug_for(cid, chals[cid]["name"])
    (d / "flag.txt").write_text(flag + "\n", encoding="utf-8")
    print(f"[ok] registrado en {d.relative_to(ROOT)}/flag.txt")
    return 0


def cmd_readmes() -> int:
    bad = 0
    for cid, d in challenge_dirs().items():
        claimed = readme_flag(d)
        stored = stored_flag(d)
        if claimed and not stored:
            print(f"[?] {cid}: README afirma {claimed} — SIN flag.txt respaldado")
            bad += 1
        elif claimed and stored and claimed != stored:
            print(f"[?] {cid}: README afirma {claimed} pero flag.txt tiene {stored}")
            bad += 1
    print(f"\n{bad} writeup(s) sin respaldo verificable.")
    return 1 if bad else 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]

    if cmd == "readmes":
        return cmd_readmes()

    plat = Platform()
    if cmd == "audit":
        return cmd_audit(plat)
    if cmd == "claim":
        if len(sys.argv) < 4:
            sys.exit("uso: ctf_platform.py claim <id> '<flag>'")
        return cmd_claim(plat, int(sys.argv[2]), sys.argv[3])
    if cmd == "submit":
        cid, flag = int(sys.argv[2]), sys.argv[3]
        print(plat.submit(cid, flag))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())