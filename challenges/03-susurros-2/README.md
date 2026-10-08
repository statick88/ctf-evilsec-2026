# 3. Susurros 2

> **Status: unsolved** — fragments recovered, final decode still ambiguous.

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
  - `DEBUG heartbeat crc32=ezNsXw== shard=9 ok` → base64 CRC32
  - `INFO etl_job stage=62 blob=c3VzdQ==` → base64 blob
  - `INFO etl_job stage=32 blob=ee0_` → plain blob
  - `INFO etl_job stage=40 blob=30736375` → hex blob
  - `INFO etl_job stage=47 blob=98.51.57.125` → ASCII-decimal IP blob
  - Plus 18 `FLAGPART` decoys (`{FAKE_0xXX}`), 4 `dns_resolver` decoys (mirror, base64, rot13, hex), 2 `auth failed_login` decoys

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

**Reconstruction result**: Fragments 1–5 concatenate to `EVIL{el_susurro_oscu`. Fragment 6 yields `b39}`, giving the candidate `el_susurro_oscub39` (wrapped in standard flag format). The platform returns **incorrect** for this candidate.

**Why fragment 6 is problematic**: The expected Spanish completion for "el susurro oscuro" would be `ro}` (yielding `el_susurro_oscuro`). Instead, fragment 6 (`98.51.57.125` → ASCII `b39}`) provides `b39}`, which:
- Does not match the linguistic completion (`ro}` vs `b39}`)
- Introduces `b39` with no clear semantic meaning
- Uses the same ASCII-decimal encoding as fragment 1, but the result is not a dictionary word

**Candidate completions tested** (all rejected by platform):
- `el_susurro_oscub39` (raw concatenation)
- `el_susurro_oscuro` (linguistic correction: replace `b39` → `ro`)
- `el_susurro_oscuro_b39` (hybrid)
- `el_susurro_oscuro39` (append numeric suffix)

**Next step**: Re-examine fragment 6's encoding. The value `98.51.57.125` decodes to ASCII `b39}` (`98='b', 51='3', 57='9', 125='}'`). Possibilities:
- The IP-like format may indicate a different decode (e.g., each octet as a separate operation)
- Fragment 6 could be a red herring / anti-automation trap
- The log may contain a 7th real fragment not yet identified (frequency >2 but pattern distinct)
- Leetspeak on `b39` (`b`=6? `3`=e? `9`=g?) yields no Spanish word

## Rejected candidate

The candidate `el_susurro_oscub39` (wrapped in standard flag format) was submitted and rejected.

**Platform verdict**: `incorrect` (returned by `/api/v1/challenges/3/submit`).  
Do not submit this candidate — it is not the accepted answer.

## Flag

No confirmed flag. The reconstruction yields a candidate that the platform rejects. Fragment 6 remains ambiguous.

## Reconstruction

```bash
$ ./solve.py
Candidate flag (NOT confirmed by platform): [candidate printed here]
Note: Fragment 6 yields 'b39}' but linguistic completion expects 'ro}'.
Platform verdict for this candidate: INCORRECT
```

The solve script streams the 7.6 MB log line-by-line (no full load), uses compiled regexes for the 6 anomaly patterns, applies the appropriate decoder, and assembles the candidate flag. **The output is a candidate, not a confirmed flag.**

## Key Takeaways

- Large logs require streaming processing (line-by-line); never `cat` 7.6 MB into memory
- Frequency analysis (`sort | uniq -c | awk '$1<=2'`) quickly isolates unique anomaly lines
- Decoys often self-identify (`FAKE`, `mirror`, `decoy`, `false`) and reveal the encoding schemes used for real fragments
- Multiple encoding layers (base64, hex, ASCII decimal, ROT13, leetspeak) can chain; decoys teach the decoder ring
- Timestamp order (file order) is the reliable sequence when fragments appear once each
- Thematic consistency ("susurros" → "el susurro oscuro") validates fragments 1–5, but fragment 6 breaks the pattern
- **Always verify candidate flags against the platform before documenting as solved**

(End of file - total 100 lines)