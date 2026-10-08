# 2. Susurros 1

**Category**: Forensic  
**Difficulty**: EASY  
**Points**: 150

## Description

> Nuestro servidor ha estado actuando de forma extraña... Entre advertencias de disco lleno y reinicios inesperados, los registros parecen susurrar fragmentos de un mensaje oculto. Sin embargo, los fragmentos están dispersos por todo el archivo, mezclados con alertas del sistema y líneas de depuración inútiles. ¿Podrás reconstruir el mensaje completo y revelar la frase secreta que los administradores escondieron en los logs?
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

- **File**: `server.log` (105 KB, 2,347 lines)
- **Log format**: `[YYYY-MM-DD HH:MM:SS] LEVEL message`
- **Normal lines**: Repeating patterns of `DEBUG System check complete`, `INFO Service restarted`, `INFO User logged in`, `WARN Disk space low`, `WARN High memory usage detected`, `ERROR Connection lost`, `ERROR Failed login attempt`
- **Anomaly**: Lines containing `FLAGPART: <fragment> es la onda` appear periodically

Sample of normal log lines:
```
[1990-08-09 10:00:00] DEBUG System check complete
[1990-08-09 10:01:00] INFO Service restarted
[1990-08-09 10:11:00] INFO FLAGPART: EVIL{ es la onda
```

## Analysis

Grepping for `FLAGPART` reveals 30 occurrences forming 6 complete cycles of 5 unique fragments each. The fragments appear in consistent timestamp order within each cycle:

| Timestamp (first cycle) | Fragment |
|------------------------|----------|
| 10:11:00 | `EVIL{` |
| 11:36:00 | `l1nux_` |
| 13:01:00 | `3s_l4_` |
| 14:26:00 | `0nd4_` |
| 15:51:00 | `nu3v4}` |

The fragments are leetspeak Spanish: `l1nux` = linux, `3s` = es, `l4` = la, `0nd4` = onda, `nu3v4` = nueva.

**Extraction rule**: Take the first occurrence of each unique `FLAGPART` fragment in timestamp order (file order), concatenate them.

## Reconstruction

```bash
$ ./solve.sh
EVIL{l1nux_3s_l4_0nd4_nu3v4}
```

The solve script uses `awk` to extract fragments after `FLAGPART: ` and before ` es la onda`, deduplicating by first occurrence.

## Flag

```
EVIL{l1nux_3s_l4_0nd4_nu3v4}
```

## Key Takeaways

- Periodic log anomalies often indicate hidden data; grep for distinctive keywords (`FLAGPART`, `flag`, `part`)
- Timestamps provide natural ordering when fragments are scattered across cycles
- Leetspeak is common in CTF flags (1=i, 3=e, 4=a, 0=o)
- Small logs can be fully loaded; deduplication via `awk` associative arrays is efficient