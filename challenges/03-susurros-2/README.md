# 3. Susurros 2

> **Status: unsolved** — closed mechanical space fully exhausted (30 submissions,
> all `incorrect`); no confirmed flag. Details below.

**Category**: Forensic  
**Difficulty**: HARD  
**Points**: 500

## Description

> Nuestro servidor ha estado actuando de forma extraña... Entre advertencias de disco lleno y reinicios inesperados, los registros parecen susurrar fragmentos de un mensaje oculto. Sin embargo, los fragmentos están dispersos por todo el archivo, mezclados con alertas del sistema y líneas de depuración inútiles. ¿Podrás reconstruir el mensaje completo y revelar la frase secreta que los administradores escondieron en los logs?
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

- **File**: `server.log` (7.6 MB, ~120,000 lines)
- **Log format**: `[YYYY-MM-DD HH:MM:SS] LEVEL message key=value key=value...`
- **Normal lines**: High-volume structured logs with fields like `host=`, `user=`, `pct=`, `backlog=`, `consumer=`, `files=`, `elapsed=`, `heap=`, `pause=`, `rows=`, `retries=`, `shard=`, `action=`, `from=`, `service=`, `job=`, `tty=`
- **Message types**: `WARN High memory usage`, `WARN cert expires`, `ERROR Connection lost`, `ERROR queue backlog`, `DEBUG gc pause`, `INFO cron ran`, `INFO backup finished`, `ERROR Failed login`, `DEBUG System check`, `WARN Disk space low`, `INFO Service restarted`, `INFO User logged in`
- **Anomalies (unique lines appearing 1-2 times each)**:
  - `INFO audit user=svc_backup ascii_dec=69.86.73.76` → "EVIL"
  - `INFO audit user=svc_backup token_hex=4556494c7b6e305f7330797d` → hex → `EVIL{n0_s0y}` — **TRAP**: byte-identical in meaning to the dns `payload_b64` decoy (`n0_s0y` = "no soy", "I'm not [it]"), planted in the trusted audit source
  - `DEBUG heartbeat crc32=ezNsXw== shard=9 ok` → base64 CRC32
  - `INFO etl_job stage=62 blob=c3VzdQ==` → base64 blob
  - `INFO etl_job stage=32 blob=ee0_` → plain blob
  - `INFO etl_job stage=40 blob=30736375` → hex blob
  - `INFO etl_job stage=47 blob=98.51.57.125` → ASCII-decimal IP blob
  - Plus 18 `FLAGPART` decoys (`{FAKE_0xXX}` ×9, `??NNN??` corrupted ×9), 4 `dns_resolver` decoys (mirror, base64, rot13, hex), 2 `auth failed_login` decoys

**Closed anomaly census** (verified by digit/hex-normalized template sweep over all
120,000 lines): exactly 13 rare templates (`heartbeat`×1, `audit`×2, `etl_job`×4,
`auth failed_login`×2, `dns_resolver`×4) plus the 2 `FLAGPART` templates (9+9).
`heartbeat`/`etl_job`/`audit` message types occur ONLY as anomaly lines. No 8th
fragment exists. `rows=`/`stage=`/`shard=` values are singletons with no linked
records; octet/row/stage numbers used as log-line pointers hit generic noise.

## Analysis

**Decoy identification**: Lines explicitly labeled `FAKE`, `mirror`, `payload_b64`, `rot13`, `token_hex` decode to strings matching the decoy pattern (e.g., `d3c0y!`, `n0_s0y`, `f4ls0_`, `ro_4`) — clearly marked as false/decoy.

**Real fragments** (6 unique lines, appear once each, in timestamp order):

| Line | Timestamp | Source | Encoding | Raw Fragment | Transformation | Decoded |
|------|-----------|--------|----------|--------------|----------------|---------|
| 1 | 02:33:53 | `audit ascii_dec` | ASCII decimal | `69.86.73.76` | ASCII decode | `EVIL` |
| 2 | 12:31:06 | `heartbeat crc32` | Base64 | `ezNsXw==` | Base64 → leetspeak (3=e) | `{el_` |
| 3 | 23:55:10 | `etl_job stage=62` | Base64 | `c3VzdQ==` | Base64 decode | `susu` |
| 4 | 08:25:01 | `etl_job stage=32` | Plain | `ee0_` | ROT13 → leetspeak (0=o) | `rro_` |
| 5 | 20:01:40 | `etl_job stage=40` | Hex | `30736375` | Hex decode → leetspeak (0=o) | `oscu` |
| 6 | 17:45:37 | `etl_job stage=47` | ASCII decimal IP | `98.51.57.125` | ASCII decode | `b39}` |

**Transformation hints from decoys**: The decoy lines explicitly use mirror/reverse, base64, ROT13, hex, ASCII decimal — each real fragment uses one of these encodings, confirming the decoding method.

**Extraction rule**: Stream the log once, match the 6 unique anomaly patterns in timestamp order (file order), decode each using its indicated method (base64, hex, ASCII decimal, ROT13, leetspeak 3=e/0=o/4=a/1=i), concatenate.

**Reconstruction result**: Fragments 1–5 concatenate to `EVIL{el_susurro_oscu`. Fragment 6 yields `b39}`, giving the candidate `el_susurro_oscub39` (wrapped in standard flag format). The platform returns **incorrect** for this candidate — and for every other candidate in the closed mechanical space (see verdict table).

**Block-structure finding**: every fragment decodes to exactly 4 chars
(`EVIL`, `{3l_`, `susu`, `rr0_`, `0scu`, `b39}`) — clearly deliberate, and it rules
out the linguistic `ro}` tail (3 chars can never come from a 4-octet dot-quad).
File/timestamp order is the only order that yields Spanish (`susurro_oscu`);
stage/rows orderings break the brace or the language. So the assembly is unique
up to leet on/off per block (2³ = 8 middles) and post-transforms of the tail.

**Fragment-6 impossibility proofs** (octets `[98,51,57,125]`, brace must survive):
- Single-byte XOR / modular-add / Caesar key `k` with `(125+k)==125` forces
  `k == identity` — the whole single-key family is dead in one stroke.
- Mirror (`}93b`) and ROT47 (`3bhN`) destroy/reposition the closing brace.
- Remaining brace-preserving transforms (`be9}`, `o39}`, `oe9}`, `r39}`,
  `e39}`, `93b}`, `beg}`, `y39}`) are un-Spanish; the Spanish-plausible ones
  were all submitted and rejected (table below).
- `rows=`/`stage=`/timestamp XOR/Vigenère keys and A1Z26-mod mappings yield
  garbage (`M\x1c\x16R`, `hqgo`, `uzfv`, …). The `crc32` value is NOT a checksum
  of any flag/part/block (59-way brute force against `0x7b336c5f`): flavor text.

**Why fragment 6 is problematic**: The expected Spanish completion for "el susurro oscuro" would be `ro}` (yielding `el_susurro_oscuro`). Instead, fragment 6 (`98.51.57.125` → ASCII `b39}`) provides `b39}`, which:
- Does not match the linguistic completion (`ro}` vs `b39}`)
- Introduces `b39` with no clear semantic meaning
- Uses the same ASCII-decimal encoding as fragment 1, but the result is not a dictionary word

**Candidate completions tested** (all rejected by platform —
`python3 scripts/lib/ctf_platform.py submit 3 '…'` → `incorrect`):

| # | Candidate | Theory |
|---|-----------|--------|
| 1 | `EVIL{el_susurro_oscub39}` | R1 raw (leet on); reconfirmed in-session |
| 2 | `EVIL{3l_susurr0_0scub39}` | R2, no leet anywhere (Susurros-1 style) |
| 3–8 | `EVIL{el_susurr0_0scub39}`, `EVIL{3l_susurro_oscub39}`, `EVIL{el_susurr0_oscub39}`, `EVIL{el_susurro_0scub39}`, `EVIL{3l_susurr0_oscub39}`, `EVIL{3l_susurro_0scub39}` | all 6 mixed leet middles × b39 |
| 9–15 | `EVIL{el_susurro_oscuro}`, `EVIL{3l_susurr0_0scur0}`, `EVIL{el_susurro_oscuro_b39}`, `EVIL{el_susurro_oscuro39}`, `EVIL{el_susurro_oscurob39}`, `EVIL{el_susurro_oscur0}`, `EVIL{el_susurro_oscuro_}` | linguistic completions |
| 16–22 | `EVIL{el_susurro_oscube9}`, `EVIL{el_susurro_oscuoe9}`, `EVIL{el_susurro_oscuo39}`, `EVIL{el_susurro_oscur39}`, `EVIL{el_susurro_oscue39}`, `EVIL{el_susurro_oscu93b}`, `EVIL{el_susurro_oscubeg}` | frag-6 post-transforms |
| 23–25 | `EVIL{n0_s0y}`, `EVIL{f4ls0_}`, `EVIL{d3c0y!}` | standalone full-flag decoys (incl. audit trap, dup of dns decoy) |
| 26 | `EVIL{EL_SUSURRO_OSCUB39}` | case variant |

(Note: an early working note cited a phantom `EVIL{n0_s30y}`; re-examination of
the raw bytes shows the audit line is 12 bytes → `EVIL{n0_s0y}`, identical to the
dns decoy. Both the phantom and the real string were submitted: incorrect.)

**Next step for the orchestrator**: the closed mechanical space (unique assembly
× 8 leet-variants × brace-preserving tail transforms) is fully exhausted with
~30 rejections. Remaining options are unprincipled (multi-byte keys, arbitrary
completions) or external (organizer hint, comparison with the 5 solving teams'
approach). Recommend parking until a new angle or hint appears — do NOT create
`flag.txt` from unconfirmed output (downstream tooling reads it as solved).

**Next step**: see the verdict table above — all of these were tested and rejected
(`98.51.57.125` decodes to ASCII `b39}` under every brace-preserving mapping;
single-key ciphers are proven impossible; order is forced by language):
- ~~The IP-like format may indicate a different decode~~ — exhausted (see proofs)
- ~~Fragment 6 could be a red herring~~ — no: brace must come from fragment 6
- ~~A 7th real fragment not yet identified~~ — census closed: none exists; the
  7th trusted-source line is the `n0_s0y` trap (dup of the dns decoy)
- ~~Leetspeak on `b39` yields no Spanish word~~ — confirmed across full map

## Rejected candidates

All 26 candidates in the table above (wrapped in standard flag format) were
submitted and rejected.

**Platform verdict**: `incorrect` (returned by `/api/v1/challenges/attempt`).
Do not resubmit these candidates — none is the accepted answer.

## Flag

No confirmed flag. The closed mechanical space is exhausted (unique assembly,
8 leet-variants, brace-preserving tail transforms, linguistic completions,
standalone decoys — ~30 submissions, all `incorrect`). `flag.txt` is
deliberately absent: creating it from unconfirmed output would mislead
downstream tooling into reading this challenge as solved.

## Reconstruction

```bash
$ ./solve.py
Candidate flag (NOT confirmed by platform): EVIL{el_susurro_oscub39}
Note: Fragment 6 yields 'b39}' but linguistic completion expects 'ro}'.
Platform verdict for this candidate AND all 30 sibling variants: INCORRECT
Audit trap line decodes to: EVIL{n0_s0y} (submitted standalone: INCORRECT)
See README.md for the closed anomaly census and full verdict table.
```

The solve script streams the 7.6 MB log line-by-line (no full load), uses compiled regexes for the 6 chain patterns plus the audit trap pattern, applies the appropriate decoder, and assembles the candidate flag. **The output is a candidate, not a confirmed flag.**

## Key Takeaways

- Large logs require streaming processing (line-by-line); never `cat` 7.6 MB into memory
- Frequency analysis (`sort | uniq -c | awk '$1<=2'`) quickly isolates unique anomaly lines
- Decoys often self-identify (`FAKE`, `mirror`, `decoy`, `false`) and reveal the encoding schemes used for real fragments
- Multiple encoding layers (base64, hex, ASCII decimal, ROT13, leetspeak) can chain; decoys teach the decoder ring
- Timestamp order (file order) is the reliable sequence when fragments appear once each
- Thematic consistency ("susurros" → "el susurro oscuro") validates fragments 1–5, but fragment 6 breaks the pattern
- **Always verify candidate flags against the platform before documenting as solved**
- A 4-octet dot-quad can only ever yield a 4-char block: length constraints alone
  can rule out whole candidate families (here, every `ro…` completion)
- For single-key ciphers, check what the key constraint on a FIXED output char
  (here the closing `}`) proves — it can kill a whole family in one stroke
- Beware traps in trusted sources: the second `audit svc_backup` line decodes to
  a full flag (`EVIL{n0_s0y}`) that duplicates a known decoy — verify bytes, not
  assumptions (an early misread added a phantom `3`)
- Negative results are results: a closed census plus an exhausted candidate
  matrix is the honest deliverable when the oracle keeps saying `incorrect`

(End of file - total 100 lines)