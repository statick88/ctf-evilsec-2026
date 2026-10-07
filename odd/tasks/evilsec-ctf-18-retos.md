# EvilSec CTF — resolver los 18 retos y documentarlos

## Objetivo

Resolver los 18 retos del evento **EvilSec CTF** (`https://evilsec-ctf.mbarete.dev/challenges`)
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

- Resolver los 18 retos y **enviar la flag a la plataforma** para validar el veredicto.
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
- Los objetivos web `192.99.247.166:8081-8085` soninstances del evento, autorizadas.

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

## Plan de trabajo

Ruta: **delegated direct** (6 frentes paralelos, uno por categoría/grupo), porque cada
frente exige leer evidencia, iterar y producir writeup + script: le cabe entero a un worker.

| Frente | Retos | Ruta |
|--------|-------|------|
| A — Web | 5, 6, 7, 8, 9 | delegado |
| B — Reversing fácil/medio | 10, 11, 12, 1 | delegado |
| C — Reversing difícil | 4 | delegado (2º pase, tras ver el patrón de B) |
| D — Forense de logs | 2, 3 | delegado |
| E — Forense de imágenes | 13, 14, 15 | delegado |
| F — OSINT | 16, 17, 18 | delegado |

## Criterios de aceptación

- [ ] Cada reto resuelto tiene su flag **validada por la plataforma** (veredicto `correct`).
- [ ] `challenges/<id>-<slug>/README.md` existe y sigue la plantilla de writeup.
- [ ] Existe un script ejecutable por reto que produce la flag sin pasos manuales.
- [ ] `README.md` raíz con tabla de progreso (18/18, puntos) y enlaces.
- [ ] `.env` y `metadata.json` sin versionar; `git status` limpio de secretos.
- [ ] Un lector externo puede clonar y entender cada solución sin contexto oral.

## Progreso

_(se actualiza al cerrar cada tarea)_

## Registro de commits

_(Conventional Commits; un commit por unidad de trabajo)_