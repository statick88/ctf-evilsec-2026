# EvilSec CTF — Progress Tracker

**Last Updated**: 2026-10-08  
**Status**: 12/21 solved · 2250 pts  
**Platform**: EvilSec CTF (CTFd)  
**Sync**: `python3 scripts/lib/ctf_platform.py audit`

---

## Quick Status

| # | Challenge | Category | Pts | Status | Flag |
|---|-----------|----------|-----|--------|------|
| 1 | MateVM 1 | Reversing | 300 | 🔴 Pending | — |
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

### 1. MateVM 1 (Reversing, 300 pts)
**Blocker**: VM emulator incomplete — success condition unknown  
**Current State**: 
- Bytecode fully parsed: 21 `tmvml` blocks, 3-byte instructions [idx, opcode, operand]
- 22 logical indices (0-21), index 1 missing, indices 1&2 missing per NOTES.md
- Opcodes: 0x14 (PUSH), 0x0d (OP with codes 8-15 = ADD/SUB/XOR/AND/OR/NOT)
- Stack-based VM, processes license char-by-char through 22 instruction sequences
- Character classification restricts input to lowercase a-z
- **Missing**: Success condition (empty stack? top=0? specific pattern?)
- **Tested**: 15+ candidates via platform, all rejected
- **Next**: Need qemu-x86_64 to trace read length & success condition, or complete VM reverse

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
**Blocker**: Real photo, stripped EXIF — no forensic geolocation  
**Current State**:
- 1200×1200 JPEG, minimal EXIF (no GPS, camera, C2PA)
- Visual: suspension bridge on costanera
- Best match: Puente Colgante de Santa Fe (rejected)
- **Submitted**: 10+ variants — all rejected
- **Insight**: No forensic geolocation possible without metadata

### 18. El Dron Olvidado (OSINT, 250 pts)
**Blocker**: AI-generated (Grok Imagine) — no geolocation possible  
**Current State**:
- 1168×784 JPEG, C2PA: `trainedAlgorithmicMedia`, Software: `Grok Imagine`
- Same generator as #16, different UUID
- **Submitted**: Thematic guess `EVIL{reserva_ecologica_costanera_sur_buenos_aires}` rejected
- **Insight**: AI drone images cannot be geolocated — synthetic scenes from prompts

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
| `scripts/lib/ctf_platform.py` | Authoritative platform sync |

---

## Next Session Priorities

1. **MateVM 1** — Install qemu-user (compile from source) to trace read length & success condition
2. **Susurros 2** — Request organizer hint; anomaly space closed
3. **Gestor Respaldos** — Read `Preferencias.php` via LFI; test MARO header + gadget chains
4. **Ecos Bit a Bit** — Test non-XOR cipher hypothesis; check IDAT CRC/palette for key
5. **MateVM 2** — Differential analysis using MateVM 1 as reference

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