# EvilSec CTF — Progress Tracker

**Last Updated**: 2026-10-09  
**Status**: 13/21 solved · 2550 pts  
**Platform**: EvilSec CTF (CTFd)  
**Sync**: `python3 scripts/lib/ctf_platform.py audit`

---

## Quick Status

| # | Challenge | Category | Pts | Status | Flag |
|---|-----------|----------|-----|--------|------|
| 1 | MateVM 1 | Reversing | 300 | ✅ Solved | `EVIL{RUST_VM_BYT3C0D3}` |
| 2 | Susurros 1 | Forensic | 150 | ✅ Solved | `EVIL{l1nux_3s_l4_0nd4_nu3v4}` |
| 3 | Susurros 2 | Forensic | 500 | 🔴 Pending | — |
| 4 | MateVM 2 | Reversing | 500 | 🔴 Pending | — |
| 5 | Banco Capybara | Web | 100 | ✅ Solved | `EVIL{bl1nd_0r_n0t_sql1_byp4ss}` |
| 6 | Facturación Capybara | Web | 150 | ✅ Solved | `EVIL{1d0r_f4ctur4_4jen4}` |
| 7 | Tablero Santuario | Web | 250 | ✅ Solved | `EVIL{ssti_j1nj4_rce_cl4ss1c}` |
| 8 | Consola API Santuario | Web | 300 | ✅ Solved | `EVIL{jwt_n0ne_4lg_c0nfus10n}` |
| 9 | Gestor Respaldos | Web | 500 | 🔴 Pending | — |
| 10 | Capybara Keygen | Reversing | 100 | ✅ Solved | `EVIL{d0tn3t_1l_d3c0mp1l3d}` |
| 11 | Capybara Gopher | Reversing | 150 | ✅ Solved | `EVIL{g0_b1n4ry_r3v3rs3d}` |
| 12 | Capybara Vault | Reversing | 250 | ✅ Solved | `EVIL{c_x0r_l00p_cr4ckm3}` |
| 13 | Ecos Postal | Forensic | 100 | ✅ Solved | `EVIL{l0v3_c4pyb4r4}` |
| 14 | Ecos Bit a Bit | Forensic | 250 | 🔴 Pending | — |
| 15 | Ecos Ruido Controlado | Forensic | 500 | 🔴 Pending | — |
| 16 | Foto del Café | OSINT | 100 | ✅ Solved | `EVIL{roma}` |
| 17 | Puente del Paseo | OSINT | 150 | 🔴 Pending | — |
| 18 | Dron Olvidado | OSINT | 250 | 🔴 Pending | — |
| 19 | Circo beat | Reversing | 500 | ✅ Solved | `EVIL{3l_4m0r_d3spu3s_d3l_c1fr4d0}` |
| 20 | 30 noches de ofrenda | Forensic | 100 | ✅ Solved | `EVIL{3l_s3cr3t0_d3l_p0mb3r0}` |
| 21 | REwrite, REpeat | Web | 500 | 🔴 Pending | — |

---

## Pending Challenges — Technical Blockers

### 3. Susurros 2 (Forensic, 500 pts)
**Blocker**: Fragment 6 decoding ambiguity  
**Current State**:
- 6 fragments extracted in timestamp order from 7.6 MB log
- Fragments 1-5 → `EVIL{el_susurro_oscu` (clear Spanish: "el susurro oscuro")
- Fragment 6: `blob=98.51.57.125` → ASCII decimal → `b39}` (expected `ro}` for "oscuro")
- **Proven**: Anomaly universe = exactly 31 lines (no 8th fragment)
- **Trap discovered**: 7th trusted-source line is a trap (`audit token_hex` → `EVIL{n0_s0y}`)
- **Proven**: Single-key ciphers on fragment 6 impossible except identity/mirror/ROT47 (brace-breaking)
- **Submitted**: 23 new candidates + history (~30 total rejections)
- **Status**: Closed mechanical space exhausted — recommend organizer hint

### 4. MateVM 2 (Reversing, 500 pts)
**Blocker**: Complete VM rewrite — 89% binary diff vs MateVM 1  
**Current State**:
- No visible strings (`MateVM`, `License`, `EVIL` all stripped)
- New bytecode format (no `tmvml` markers), likely encrypted/split
- Anti-tamper: control flow flattening, opaque predicates
- **Next**: Differential analysis from MateVM 1 anchors (11% identical bytes)

### 9. Gestor de Respaldos Capybara (Web, 500 pts)
**Blocker**: PHP deserialization — `plantilla` LFI not triggering output  
**Current State**:
- `pref` cookie = `base64(serialize(Preferencias))` with `tema` + `plantilla` (default `N;`)
- `<!--AGENT-CAPYBARA-MARO-->` comment in HTML — likely required header/gadget
- Tested: `php://filter`, `data://`, `phar://`, path traversal, `SplFileObject`, gadget chains
- All payloads return normal page (3697 bytes) — deserialization in try-catch `@`
- Cookie resets to default after each request
- **Hypothesis**: `plantilla` used in `__destruct()`/`__toString()` but output discarded
- **Next**: Read `Preferencias.php` via LFI to identify magic methods; test MARO header

### 14. Ecos Ocultos: Bit por Bit (Forensic, 250 pts)
**Blocker**: XOR key derivation for per-row LSB steganography  
**Current State**:
- 480×640 PNG, 640 rows × 60 bytes/row per channel (R/G/B)
- R/G channels: 639 unique ciphertexts, rows 0-14 share constant R^G XOR
- Row 0: 32/60 key bytes known (5 from `EVIL{...}` format + 27 from zero-ciphertext)
- **Key discovery**: `G_ct[r] = R_ct[r] ^ C` (constant C) for rows 0-14
- **Key insight**: Plaintext is binary/image-like, NOT ASCII text (frequency analysis ~0.43 printable)
- **Exhausted**: ~30k phrases + all standard PRNG/LCG/XOF families, all packing variants
- **Best lead**: Non-XOR cipher (block cipher + sync-bit flips), or key in IDAT CRCs/palette

### 15. Ecos Ocultos: Ruido Controlado (Forensic, 500 pts)
**Blocker**: Procedural noise seed recovery  
**Current State**:
- PNG with corrupted IHDR CRC (fixed: 0x65fdde11)
- 80 hidden rows in IDAT (original 430×625, cropped to 350×625)
- Procedural 8×8 value noise, corner grid 44×79 / 54×79
- G channel corners: permutation table (all 256 values)
- **Tested**: 15 seed candidates (dimensions, CRCs, file size, phrases) — all rejected
- **Next**: Brute-force noise seed from image properties; implement noise generator

### 17. El Puente del Paseo (OSINT, 150 pts)
**Blocker**: Real photo, stripped EXIF — no metadata geolocation  
**Current State**:
- 1200×1200 JPEG, minimal EXIF (no GPS, camera, C2PA)
- Visual: suspension bridge on costanera / waterfront promenade
- Best prior match: Puente Colgante de Santa Fe / Ing. Marcial Candioti, but submitted variants were rejected
- **Submitted**: 10+ variants — all rejected
- **Next**: Re-open as visual comparison, not metadata forensics; compare tower geometry, cable pattern, shoreline, promenade railings/lights, and official bridge naming before any new submit

### 18. El Dron Olvidado (OSINT, 250 pts)
**Blocker**: AI-generated image gives no metadata location; visual landmark still unresolved  
**Current State**:
- 1168×784 JPEG, C2PA: `trainedAlgorithmicMedia`, Software: `Grok Imagine`
- Same generator class as #16, but AI provenance does not prove there is no intended landmark
- Thematic guess `EVIL{reserva_ecologica_costanera_sur_buenos_aires}` rejected
- **Next**: Treat as visual OSINT: compare aerial shoreline, green shore, pier/peninsula shape, road grid, and nearby urban layout against Argentine waterfront parks/reserves

### 21. REwrite, REpeat (Web, 500 pts)
**Blocker**: Apache 2.4.55 exposed, but no exploitable rewrite/proxy route found yet  
**Current State**:
- Root returns default `It works!` page; `Server: Apache/2.4.55 (Unix)`
- `TRACE` is enabled and reflects request headers, but direct `/flag`, `/api`, `/rewrite`, `/repeat`, common paths, and Host variants returned default/404 behavior
- Challenge wording points to frontend sanitization before backend processing: likely parser/rewrite mismatch
- External research aligns with CVE-2023-25690 class: Apache 2.4.0–2.4.55 + `mod_rewrite`/`mod_proxy` variable substitution can enable request splitting/smuggling
- **Next**: Find the hidden rewrite prefix or backend route, then test CRLF/request-smuggling payloads with strict rate limits and captured request/response evidence

---

## Files Created/Updated

| Path | Description |
|------|-------------|
| `ODD_PROGRESS.md` | This tracker |
| `challenges/01-matevm-1/NOTAS.md` | Handoff notes (qemu setup, bytecode structure) |
| `challenges/03-susurros-2/solve.py` | Streaming log parser + trap detection |
| `challenges/03-susurros-2/README.md` | Closed census, trap correction, verdict table |
| `challenges/09-gestor-de-respaldos-capybara/README.md` | PHP deserialization attempts, MARO hint |
| `challenges/09-gestor-de-respaldos-capybara/solve.py` | Basic LFI attempt script |
| `challenges/14-ecos-ocultos-bit-por-bit/extracted_data.json` | All 640 rows R/G/B ciphertexts |
| `challenges/14-ecos-ocultos-bit-por-bit/README.md` | Corrected analysis, ruled-out list |
| `challenges/15-ecos-ocultos-ruido-controlado/ruido_repaired.png` | Fixed PNG (valid IHDR CRC) |
| `challenges/19-circo-beat/README.md` | CSS colors → shellcode → AES-256-CBC writeup |
| `challenges/19-circo-beat/solve.py` | Static decoder for #19 |
| `challenges/20-30-noches-de-ofrenda/README.md` | Zero-width Unicode stego writeup |
| `challenges/20-30-noches-de-ofrenda/solve.py` | Zero-width bitstream decoder for #20 |
| `scripts/lib/ctf_platform.py` | Authoritative platform sync |

---

## Next Session Priorities

1. **REwrite, REpeat (#21)** — Find hidden rewrite/proxy route, then test CVE-2023-25690-style request splitting safely
2. **Susurros 2 (#3)** — Request organizer hint or identify special rule for fragment 6; current anomaly space is closed
3. **Gestor Respaldos (#9)** — Read/derive `Preferencias` magic methods; test MARO header + gadget chains
4. **Ecos Bit a Bit (#14)** — Test non-XOR cipher hypothesis; check IDAT CRC/palette for key
5. **MateVM 2 (#4)** — Differential analysis using MateVM 1 as reference

---

## Commands Reference

```bash
# Platform interaction
source scripts/ctf.sh
ctf-list                    # Challenge table
ctf-info <id>               # Challenge details
ctf-submit <id> 'EVIL{...}' # Submit flag
ctf-solved                  # Solved by this session

# Audit & claim
python3 scripts/lib/ctf_platform.py audit
python3 scripts/lib/ctf_platform.py claim <id> 'EVIL{...}'

# Run individual solvers
cd challenges/XX-name && python3 solve.py
```