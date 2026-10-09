# 4. MateVM 2

**Categoría**: Reversing (`REVERSING`)
**Dificultad**: HARD
**Puntos**: 500
**Estado**: resuelto y validado por la plataforma

## Enunciado

> Un desarrollador escribió su propio sistema de licencias en Rust.
> Dice que nadie puede romperlo porque no hay ninguna comparación directa de la flag.
>
> ¿Podés recuperar la licencia válida?
>
> **Formato de flag:** `EVIL{...}`

## Artefactos

- `matevm2`

## Análisis

La recuperación se hizo mediante emulación estática de la VM. El proceso recuperó una
licencia de 37 caracteres y permitió reconstruir el bytecode cifrado.

El punto decisivo fue corregir la tabla de direcciones de los selectores:

- el selector `3` usa como base `0x59d4`;
- los selectores `0`, `1` y `2` usan desplazamientos con signo desde la base `0x6c48`.

Con esa tabla corregida, el bytecode descifrado produce la licencia válida. El resultado
fue confirmado mediante `python3 scripts/lib/ctf_platform.py claim 4 ...`; además,
`flag.txt` quedó registrado por la plataforma.

## Reproducción

```bash
python3 solve.py
```

`solve.py` es un reproductor estático mínimo del resultado validado; no intenta ser un
descompilador completo de la VM.

## Flag

```text
EVIL{STATEFUL_VM_BYTECODE_2026}
```

## Aprendizajes

- En una VM ofuscada, una tabla de saltos aparentemente cercana puede mezclar bases y
desplazamientos con convenciones distintas.
- Confirmar el mapeo de selectores antes de interpretar el bytecode evita propagar una
clave incorrecta por toda la emulación.
