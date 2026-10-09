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
  printf '%s' "$out" | tr -d '\r' | grep -oE 'EVIL\{[^}]*\}' | sort -u | paste -s -d ' ' -
}

printf '%-46s %-11s %-9s %s\n' RETO FLAG.TXT SCRIPT SALIDA
for dir in challenges/*/; do
  name="$(basename "$dir")"

  # La verdad es flag.txt: solo existe si la plataforma confirmó la flag.
  # El script puede imprimir conjeturas, así que no se usa como veredicto.
  stored="—"
  [[ -f "$dir/flag.txt" ]] && stored="$(tr -d '[:space:]' < "$dir/flag.txt")"

  script=""
  for cand in "$dir"solve.py "$dir"solve.sh; do
    if [[ -f "$cand" ]]; then script="$cand"; break; fi
  done

  if [[ -z "$script" ]]; then
    printf '%-46s %-11s %-9s %s\n' "$name" "$stored" "SIN" "(sin script)"
    continue
  fi

  out="$(run_one "$dir" "$script")"
  out="$(printf '%s' "$out" | tr -d '\r' | grep -oE 'EVIL\{[A-Za-z0-9_!$@#*.,+-]{2,96}\}' | sort -u | paste -s -d ' ' -)"

  if [[ "$stored" != "—" ]]; then
    if printf '%s' "$out" | grep -qF "$stored"; then
      verdict="coincide"
    else
      verdict="DIFIERE"
    fi
  else
    verdict="sin flag"
  fi
  [[ -z "$out" ]] && out="(no imprime flag)"
  printf '%-46s %-11s %-9s %s\n' "$name" "$stored" "$verdict" "${out:0:44}"
done