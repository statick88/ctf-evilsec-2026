# EvilSec CTF — retos resueltos y documentados

Writeups reproducibles del evento **EvilSec CTF**. Cada reto vive en su propia carpeta con
el método, el porqué de la vulnerabilidad y un script que devuelve la flag sin pasos
manuales.

> **Regla de este repo:** una flag existe si y solo si existe `challenges/<slug>/flag.txt`.
> Ese fichero lo crea `scripts/lib/ctf_platform.py claim`, que solo escribe después de que
> la plataforma responda `correct`. Ningún writeup afirma una flag sin ese respaldo.

## Estado

Verificado contra la plataforma del evento con
`python3 scripts/lib/ctf_platform.py audit`, que reconcilia el repo contra el scoreboard y
vuelve a enviar cada `flag.txt`:

- **12 / 21 retos resueltos · 2250 puntos** (a fecha de la última verificación)

| # | Categoría | Pts | Nombre | Estado | Flag |
|---|-----------|-----|--------|--------|------|
| 1 | Reversing | 300 | MateVM 1 | pendiente | — |
| 2 | Forense | 150 | Susurros 1 | **resuelto** | `EVIL{l1nux_3s_l4_0nd4_nu3v4}` |
| 3 | Forense | 500 | Susurros 2 | pendiente | — |
| 4 | Reversing | 500 | MateVM 2 | pendiente | — |
| 5 | Web | 100 | Banco Capybara | **resuelto** | `EVIL{bl1nd_0r_n0t_sql1_byp4ss}` |
| 6 | Web | 150 | Facturación Capybara | **resuelto** | `EVIL{1d0r_f4ctur4_4jen4}` |
| 7 | Web | 250 | Tablero del Santuario | **resuelto** | `EVIL{ssti_j1nj4_rce_cl4ss1c}` |
| 8 | Web | 300 | Consola API del Santuario | **resuelto** | `EVIL{jwt_n0ne_4lg_c0nfus10n}` |
| 9 | Web | 500 | Gestor de Respaldos | pendiente | — |
| 10 | Reversing | 100 | Capybara Keygen | **resuelto** | `EVIL{d0tn3t_1l_d3c0mp1l3d}` |
| 11 | Reversing | 150 | Capybara Gopher | **resuelto** | `EVIL{g0_b1n4ry_r3v3rs3d}` |
| 12 | Reversing | 250 | Capybara Vault | **resuelto** | `EVIL{c_x0r_l00p_cr4ckm3}` |
| 13 | Forense | 100 | Ecos Ocultos: Postal | **resuelto** | `EVIL{l0v3_c4pyb4r4}` |
| 14 | Forense | 250 | Ecos Ocultos: Bit por Bit | pendiente | — |
| 15 | Forense | 500 | Ecos Ocultos: Ruido Controlado | pendiente | — |
| 16 | OSINT | 100 | La foto del café | **resuelto** | `EVIL{roma}` |
| 17 | OSINT | 150 | El puente del paseo | pendiente | — |
| 18 | OSINT | 250 | El dron olvidado | pendiente | — |
| 19 | Reversing | 500 | Circo beat | **resuelto** | `EVIL{3l_4m0r_d3spu3s_d3l_c1fr4d0}` |
| 20 | Forense | 100 | 30 noches de ofrenda | **resuelto** | `EVIL{3l_s3cr3t0_d3l_p0mb3r0}` |
| 21 | Web | 500 | REwrite, REpeat | pendiente | — |

Los retos pendientes tienen writeup con el progreso real obtenido y están marcados
`Status: unsolved`. No contienen flags inventadas.

## Uso

```bash
source scripts/ctf.sh     # carga la sesión de .env

ctf-list                  # tabla de retos del evento
ctf-info 7                # enunciado, pistas y ficheros de un reto
ctf-fetch-all             # descarga los artefactos (ya están en el repo)
ctf-submit 7 'EVIL{...}'  # envía una flag y muestra el veredicto
ctf-solved                # retos ya resueltos por esta sesión

# reconciliación repo <-> plataforma (autoritativa)
python3 scripts/lib/ctf_platform.py audit
python3 scripts/lib/ctf_platform.py claim <id> 'EVIL{...}'   # registra solo si es correct

# reejecuta cada script de resolución y muestra qué flag produce
bash scripts/verify-all.sh
```

`.env` (URL y cookie de sesión) está en `.gitignore` y nunca se versiona.

## Estructura

```
challenges/<id>-<slug>/
  FICHA.md      enunciado y metadatos, generados de la plataforma
  README.md     writeup: recon -> análisis -> explotación -> flag
  solve.py|sh   script ejecutable que produce la flag
  flag.txt      la flag, solo si la plataforma la confirmó
scripts/
  ctf.sh              helper de plataforma (bash y zsh)
  verify-all.sh       reejecuta todas las soluciones
  lib/                utilidades: auditoría, fichas, listados
docs/                 guías por categoría
odd/tasks/            documento de feature y plan de trabajo
```

## Dos trampas que costaron tiempo (documentadas para que no se repitan)

**1. CTFd exige `CSRF-Token` en todo POST.** Sin ese header Flask-WTF responde `403` con
el texto *"You don't have the permission to access the requested resource"*, que parece un
problema de permisos o de no tener equipo — y no lo es. El nonce va embebido en el estado
inicial que el HTML sirve. `scripts/ctf.sh` lo extrae y lo manda. Consecuencia práctica:
mientras faltara ese header no existía veredicto posible, y cualquier "confirmado" era
inventado.

**2. Las imágenes de dos retos OSINT son generadas por IA.** `#16` y `#18` llevan manifiesto
C2PA con `Grok Imagine` y calidad JPEG 95; `#17` es una foto real con calidad 85. La
diferencia de pipeline se detecta comparando la calidad JPEG, y decide si buscar metadatos
o mirar el paisaje.

## Guías por categoría

- [`docs/web/`](docs/web/) — SQLi UNION para escalonar privilegios, IDOR, SSTI en Jinja2,
  confusión de algoritmo en JWT.
- [`docs/forensics/`](docs/forensics/) — fragmentos en logs, estego en PNG.
- [`docs/reversing/`](docs/reversing/) — XOR de un byte, recuperación de clave algebraica.
- [`docs/osint/`](docs/osint/) — geolocalización por contenido visual.
