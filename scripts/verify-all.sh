#!/usr/bin/env bash
# Ejecuta cada script de resolución y muestra qué flag produce.
#
# Esto es EVIDENCIA LOCAL, no confirmación del veredicto: la plataforma sólo
# confirma cuando la sesión pertenece a un equipo (si no, el endpoint de
# submission responde 403). Para web, que la app muestre la flag en su
# respuesta ya es prueba; para retos de fichero, es una reconstrucción
# previamente razonada.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$ROOT" || exit 1

run_one() {
  local dir="$1" script="$2"
  local base out
  base="$(basename "$script")"
  if [[ "$script" == *.py ]]; then
    out="$(cd "$dir" && timeout 120 python3 "$base" 2>&1)"
  else
    out="$(cd "$dir" && timeout 120 bash "$base" 2>&1)"
  fi
  printf '%s' "$out" | tr -d '\r' | grep -oE 'EVIL\{[^}]*\}' | sort -u | paste -sd' '
}

printf '%-46s %-9s %s\n' RETO ESTADO FLAG
for dir in challenges/*/; do
  name="$(basename "$dir")"
  script=""
  for cand in "$dir"solve.py "$dir"solve.sh; do
    if [[ -f "$cand" ]]; then script="$cand"; break; fi
  done

  if [[ -z "$script" ]]; then
    printf '%-46s %-9s %s\n' "$name" "SIN" "(sin script)"
    continue
  fi

  out="$(run_one "$dir" "$script")"
  if [[ -z "$out" ]]; then
    printf '%-46s %-9s %s\n' "$name" "PENDIENTE" "(no produce flag)"
  elif printf '%s' "$out" | grep -qE '_{3,}|\.\.\.'; then
    printf '%-46s %-9s %s\n' "$name" "PARCIAL" "$out"
  else
    printf '%-46s %-9s %s\n' "$name" "OK" "$out"
  fi
done