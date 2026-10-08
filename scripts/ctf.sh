#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# ctf.sh — helper único para el CTF de EvilSec (bash y zsh).
#
#   source scripts/ctf.sh
#   ctf-list                 -> tabla de retos (id, categoría, puntos, resueltos)
#   ctf-info <id>            -> ficha del reto: descripción, pistas, ficheros, URLs
#   ctf-fetch <id>           -> descarga el/los archivo(s) del reto a challenges/
#   ctf-fetch-all            -> descarga todos los retos
#   ctf-submit <id> <flag>   -> envía la flag a la plataforma y muestra el veredicto
#   ctf-solved               -> lista los retos ya resueltos
#
# La sesión se lee de .env (url + session), que NUNCA se versiona.
# ---------------------------------------------------------------------------
set -euo pipefail

# BASH_SOURCE no existe en zsh; cuando se hace `source`, $0 es el propio archivo.
_ctf_self="${BASH_SOURCE[0]:-$0}"
CTF_ROOT="$(cd "$(dirname "$_ctf_self")/.." && pwd)"
CTF_LIB="$CTF_ROOT/scripts/lib"
ENV_FILE="${CTF_ENV:-$CTF_ROOT/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[!] No encuentro $ENV_FILE (variables url / session)" >&2
  return 1 2>/dev/null || exit 1
fi
# shellcheck disable=SC1090
source "$ENV_FILE"
# .env usa `url=` y `session=`; aceptamos también los nombres largos.
CTF_URL="${CTF_URL:-${url:-}}"
CTF_SESSION="${CTF_SESSION:-${session:-}}"
: "${CTF_URL:?CTF_URL/url no definida en .env}"
: "${CTF_SESSION:?CTF_SESSION/session no definida en .env}"
# .env apunta a .../challenges; la API vive en el origen.
CTF_URL="$(python3 -c 'import sys,urllib.parse as u; print(u.urlsplit(sys.argv[1]).scheme+"://"+u.urlsplit(sys.argv[1]).netloc)' "$CTF_URL")"

# El SPA de CTFd manda `CSRF-Token` en TODAS las peticiones, tomado del estado
# inicial que se sirve embebido en el HTML. Sin ese header, Flask-WTF responde
# 403 con el mensaje "You don't have the permission to access the requested
# resource", que parece un problema de permisos pero en realidad es CSRF.
ctf-csrf() {
  curl -sS -b "session=${CTF_SESSION}" "${CTF_URL}/challenges" \
    | grep -oE "csrfNonce': \"[a-f0-9]+\"" | head -1 \
    | grep -oE '[a-f0-9]{32,}'
}
CTF_CSRF="$(ctf-csrf)"
export CTF_CSRF

_ctf() {
  if [[ -n "${CTF_CSRF:-}" ]]; then
    curl -sS -b "session=${CTF_SESSION}" -H "CSRF-Token: ${CTF_CSRF}" \
         -H "Accept: application/json" "$@"
  else
    curl -sS -b "session=${CTF_SESSION}" -H "Accept: application/json" "$@"
  fi
}

ctf-list()   { _ctf "${CTF_URL}/api/v1/challenges" | python3 "$CTF_LIB/list.py"; }
ctf-info()   { _ctf "${CTF_URL}/api/v1/challenges/${1:?uso: ctf-info <id>}" \
                 | python3 "$CTF_LIB/info.py"; }
ctf-slug()   { _ctf "${CTF_URL}/api/v1/challenges/${1:?uso: ctf-slug <id>}" \
                 | python3 "$CTF_LIB/slug.py"; }
ctf-solved() { _ctf "${CTF_URL}/api/v1/challenges" | python3 "$CTF_LIB/solved.py"; }

ctf-submit() {
  local id="${1:?uso: ctf-submit <id> <flag>}"
  local flag="${2:?falta la flag}"
  local body
  body="$(python3 -c 'import json,sys; print(json.dumps({"challenge_id":int(sys.argv[1]),"submission":sys.argv[2]}))' "$id" "$flag")"
  _ctf -X POST "${CTF_URL}/api/v1/challenges/attempt" \
       -H 'Content-Type: application/json' -d "$body" \
    | python3 "$CTF_LIB/submit.py"
}

ctf-fetch() {
  local id="${1:?uso: ctf-fetch <id>}"
  local dest="${2:-}"
  [[ -z "$dest" ]] && dest="$(ctf-slug "$id")"
  local dir="$CTF_ROOT/challenges/$dest"
  mkdir -p "$dir"
  _ctf "${CTF_URL}/api/v1/challenges/${id}" > "$dir/metadata.json"

  local urls name
  urls="$(python3 -c 'import json,sys; print("\n".join(json.load(open(sys.argv[1]))["data"].get("files") or []))' "$dir/metadata.json")"
  if [[ -z "$urls" ]]; then
    echo "[ok] reto $id (reto remoto, sin ficheros) -> challenges/$dest/"
    return 0
  fi
  while IFS= read -r u; do
    [[ -z "$u" ]] && continue
    name="$(basename "${u%%\?*}")"
    _ctf "${CTF_URL}${u}" -o "$dir/$name"
    echo "[ok] $name ($(stat -c%s "$dir/$name") bytes)"
  done <<< "$urls"
  echo "[ok] reto $id -> challenges/$dest/"
}

ctf-fetch-all() {
  local ids id
  ids="$(_ctf "${CTF_URL}/api/v1/challenges" | python3 -c \
        'import json,sys; print("\n".join(str(c["id"]) for c in sorted(json.load(sys.stdin)["data"], key=lambda c: c["id"])))')"
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    ctf-fetch "$id" || echo "[warn] no se pudo descargar el reto $id"
    sleep 0.3
  done <<< "$ids"
}