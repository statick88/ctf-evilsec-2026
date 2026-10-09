# EvilSec CTF — resolver los retos y documentarlos

## Objetivo

Resolver los retos del evento **EvilSec CTF** (`https://evilsec-ctf.mbarete.dev/challenges`)
y dejar cada solución reproducible y explicada en un repositorio navegable: por reto,
un `README.md` con el método, el porqué de la vulnerabilidad y un script ejecutable
que devuelve la flag sin pasos manuales.

## Problema / por qué

Sin documentación, un writeup de CTF es una lista de comandos sin contexto: nadie puede
reproducirlo ni entender por qué funciona. El objetivo es que cada `challenges/<id>-<slug>/`
sea autocontenido y que el repositorio completo se pueda leer de arriba abajo como guía
de estudio por categoría.

## Alcance

**Dentro de alcance**

- Resolver los retos y **enviar la flag a la plataforma** para validar el veredicto.
- Un `README.md` por reto: categoría, enunciado, recon, análisis, explotación, flag,
  script de resolución y key takeaways.
- Un script ejecutable por reto (`solve.sh` / `solve.py`) que produce la flag.
- Índice raíz `README.md` con tabla de progreso, puntos y enlaces a cada writeup.
- Guías por categoría (`docs/`) que destilen el patrón compartido de los retos similares.

**Fuera de alcance**

- Infraestructura, CI, o publicación del repositorio (decisión del usuario).
- Retos de otros eventos.

## Restricciones

- La sesión vive en `.env` y está en `.gitignore`. Nunca versionar credenciales ni los
  tokens de descarga que vienen en `metadata.json`.
- Todo artefacto textual (README, scripts, comentarios) en **inglés profesional neutro**
  o español neutro según el contexto ya existente; nunca jerga de persona.
- Nada de fuerza bruta masiva ni DoS contra los objetivos: son retos EASY/MEDIUM con
  vulnerabilidades web lógicas y reversing estático.
- Los objetivos web `192.99.247.166:8081-8086` son instancias del evento, autorizadas.

## Mapa de retos

| # | Categoría | Pts | Dificultad | Nombre | Enfoque esperado |
|---|-----------|-----|------------|--------|------------------|
| 1 | REVERSING | 300 | MEDIUM | MateVM 1 | VM propia en Rust, licencia sin comparación directa |
| 2 | FORENSIC | 150 | EASY | Susurros 1 | Fragmentos dispersos en `server.log` |
| 3 | FORENSIC | 500 | HARD | Susurros 2 | Log de 8 MB, mensaje oculto entre ruido |
| 4 | REVERSING | 500 | HARD | MateVM 2 | VM propia, más endurecida |
| 5 | WEB | 100 | EASY | Banco Capybara | Auth bypass → rol admin |
| 6 | WEB | 150 | EASY | Facturación Capybara | IDOR en facturas (capybarito/capybarito123) |
| 7 | WEB | 250 | MEDIUM | Tablero del Santuario | SSTI en saludo, flag en config |
| 8 | WEB | 300 | MEDIUM | Consola API | Escalada de privilegios vía rol en token |
| 9 | WEB | 500 | HARD | Gestor de Respaldos | Tema de la app → superficie de ataque inesperada |
| 10 | REVERSING | 100 | EASY | Capybara Keygen | .NET DLL, decompilar y resolver el validador |
| 11 | REVERSING | 150 | EASY | Capybara Gopher | Binario Go, flag no en texto plano |
| 12 | REVERSING | 250 | MEDIUM | Capybara Vault | ELF 64 stripped, lógica de validación |
| 13 | FORENSIC | 100 | EASY | Ecos Ocultos: Postal | Metadatos/archivos embebidos en PNG |
| 14 | FORENSIC | 250 | MEDIUM | Ecos Ocultos: Bit por Bit | LSB + cifrado |
| 15 | FORENSIC | 500 | HARD | Ecos Ocultos: Ruido | Imagen recortada, estego en ruido |
| 16 | OSINT | 100 | EASY | La foto del café | Geolocalización de foto |
| 17 | OSINT | 150 | EASY | El puente del paseo | Identificar puente en costanera |
| 18 | OSINT | 250 | MEDIUM | El dron olvidado | Lugar exacto de toma |
| 19 | REVERSING | 500 | HARD | Circo beat | CSS color stream → shellcode → CryptoAPI |
| 20 | FORENSIC | 100 | EASY | 30 noches de ofrenda | Unicode invisible / zero-width stego |
| 21 | WEB | 500 | HARD | REwrite, REpeat | Apache rewrite/proxy parser mismatch |
| 22 | FORENSIC | 500 | HARD | Exfil Silenciosa | Exfiltración en DNS-over-TLS reconstruida desde PCAP |

## Plan de trabajo

Ruta: **delegated direct** (6 frentes paralelos, uno por categoría/grupo), porque cada
frente exige leer evidencia, iterar y producir writeup + script: le cabe entero a un worker.

| Frente | Retos | Ruta |
|--------|-------|------|
| A — Web | 5, 6, 7, 8, 9, 21 | delegado |
| B — Reversing fácil/medio | 10, 11, 12, 1, 19 | delegado |
| C — Reversing difícil | 4 | delegado (2º pase, tras ver el patrón de B) |
| D — Forense de logs/texto | 2, 3, 20 | delegado |
| E — Forense de imágenes/red | 13, 14, 15, 22 | delegado |
| F — OSINT | 16, 17, 18 | delegado |

## Criterios de aceptación

- [ ] Cada reto resuelto tiene su flag **validada por la plataforma** (veredicto `correct`).
- [ ] `challenges/<id>-<slug>/README.md` existe y sigue la plantilla de writeup.
- [ ] Existe un script ejecutable por reto que produce la flag sin pasos manuales.
- [ ] `README.md` raíz con tabla de progreso (22 retos visibles, puntos) y enlaces.
- [ ] `.env` y `metadata.json` sin versionar; `git status` limpio de secretos.
- [ ] Un lector externo puede clonar y entender cada solución sin contexto oral.

## Progreso

Estado verificado contra la plataforma (`scripts/lib/ctf_platform.py audit`).

| # | Estado oficial | Flag | Nota |
|---|----------------|------|------|
| 2 | RESUELTO | `EVIL{l1nux_3s_l4_0nd4_nu3v4}` | FLAGPART dedupe |
| 5 | RESUELTO | `EVIL{bl1nd_0r_n0t_sql1_byp4ss}` | SQLi UNION, 4 columnas |
| 6 | RESUELTO | `EVIL{1d0r_f4ctur4_4jen4}` | IDOR factura id=1 |
| 7 | RESUELTO | `EVIL{ssti_j1nj4_rce_cl4ss1c}` | SSTI Jinja2 `{{config}}` |
| 8 | RESUELTO | `EVIL{jwt_n0ne_4lg_c0nfus10n}` | JWT `alg=none` |
| 10 | RESUELTO | `EVIL{d0tn3t_1l_d3c0mp1l3d}` | .NET + XOR |
| 11 | RESUELTO | `EVIL{g0_b1n4ry_r3v3rs3d}` | Go + XOR 0x5A |
| 12 | RESUELTO | `EVIL{c_x0r_l00p_cr4ckm3}` | clave por inversión algebraica |
| 13 | RESUELTO | `EVIL{l0v3_c4pyb4r4}` | base64 en chunk tEXt |
| 16 | RESUELTO | `EVIL{roma}` | el encuadre muestra el Colosseo |
| 1 | RESUELTO | `EVIL{RUST_VM_BYT3C0D3}` | VM 3-byte: decrypt bytecode + solve per-character constraints |
| 3 | pendiente | — | 5 de 6 fragmentos; el 6º no cuadra |
| 4 | RESUELTO | `EVIL{STATEFUL_VM_BYTECODE_2026}` | Emulación estática: selector 3 base `0x59d4`; 0..2 offsets con signo desde `0x6c48` |
| 9 | pendiente | — | PHP deserialización; 1 solo solve en el evento |
| 14 | pendiente | — | LSB con periodo 60, clave parcial |
| 15 | pendiente | — | PNG restaurado a 430 filas; unfilter corregido; ruido procedural |
| 17 | pendiente | — | foto real (q85), puente atirantado en A |
| 18 | pendiente | — | imagen IA (Grok), plaza con estatua ecuestre |
| 19 | RESUELTO | `EVIL{3l_4m0r_d3spu3s_d3l_c1fr4d0}` | CSS colors → shellcode → AES-256-CBC |
| 20 | RESUELTO | `EVIL{3l_s3cr3t0_d3l_p0mb3r0}` | Zero-width Unicode stego |
| 21 | pendiente | — | Apache 2.4.55 / mod_rewrite smuggling hypothesis; no route found yet |
| 22 | RESUELTO | `EVIL{d0t_tunnel1ng_r3ass3mbl3d_by_txid}` | SMTP/SSLKEYLOGFILE → DNS-over-TLS → Base32 reensamblado por ID de transacción |

**15/22 confirmadas por la plataforma · 3550 puntos.**

### Dos errores metodológicos que ya costaron tiempo (no repetirlos)

1. **El 403 no era falta de equipo.** CTFd exige header `CSRF-Token` en todo POST;
   sin él Flask-WTF devuelve 403 con un mensaje que parece de permisos. `scripts/ctf.sh`
   lo obtiene del estado inicial del HTML. Consecuencia: los workers que "reportaron"
   veredicto `correct` antes de arreglar esto estaban inventando.
2. **Un writeup que afirma una flag rechazada es peor que no tener writeup.** Los retos
   3, 16, 17 y 18 tenían writeups con flags que la plataforma rechazó. El auditor
   (`audit`) ahora compara README contra `flag.txt` y contra la plataforma, y `flag.txt`
   sólo se escribe tras un `correct` confirmado.

## Pendientes activos

| # | Reto | Bloqueo | Siguiente acción |
|---|------|---------|------------------|
| 3 | Susurros 2 | Fragmento 6 ambiguo y candidatos rechazados | Pista / regla especial para fragmento final |
| 9 | Gestor Respaldos | Deserialización sin salida visible | Magic methods + MARO header |
| 14 | Ecos Bit por Bit | LSB extraído, cifrado/key pendiente | Probar no-XOR y claves PNG |
| 15 | Ecos Ruido | Bitplanes directos descartados con unfilter correcto | Reconstruir generador/semilla de ruido |
| 17 | Puente del paseo | Sin metadata; candidatos Santa Fe rechazados | Comparación visual precisa |
| 18 | Dron olvidado | AI/C2PA sin GPS; Costanera Sur rechazada | OSINT visual sobre costa/parque/trama urbana |
| 21 | REwrite, REpeat | Ruta rewrite/proxy no identificada | Enumerar prefijo y probar smuggling acotado |

### Regla de oro del repo

Una flag existe en el repo si y solo si existe `challenges/<slug>/flag.txt`, y ese
fichero lo crea `ctf_platform.py claim`, que sólo escribe tras `correct` de la
plataforma. Ni los writeups ni los scripts se adelantan a esa confirmación.
