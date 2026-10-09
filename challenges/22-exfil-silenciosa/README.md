# 22. Exfil Silenciosa

**Categoría**: Forensic (`FORENSIC`)
**Dificultad**: HARD
**Puntos**: 500
**Estado**: resuelto y validado por la plataforma

## Enunciado

Una captura de red mezcla tráfico HTTP, SMTP y conexiones TLS. El objetivo es
reconstruir la evidencia exfiltrada.

## Ruta de resolución

1. En `captura.pcapng`, el flujo HTTP de *heartbeat* devuelve una configuración JSON
   con `QzItS3I0azNuIzIwMjYh`. Al decodificar Base64 se obtiene la contraseña
   `C2-Kr4k3n#2026!`.
2. El flujo SMTP 7 contiene el adjunto `trace_output.dat`, que es un archivo
   `SSLKEYLOGFILE`.
3. Esa clave permite descifrar el flujo TLS en el puerto 10853. La aplicación dentro de
   TLS es DNS-over-TLS.
4. Las consultas TXT sospechosas bajo `cdn-sync.io` y `stats-collector.net` llevan
   fragmentos Base32 en sus primeras etiquetas.
5. Los fragmentos deben reensamblarse por ID de transacción DNS, no por orden de
   paquete. Después de decodificar Base32 se recupera un ZIP cifrado.
6. Al extraer el ZIP con la contraseña recuperada aparece `flag.txt`.

La flag se validó oficialmente mediante el comando `claim`; `flag.txt` existe como
registro local de esa validación.

## Reproducción

```bash
python3 solve.py
```

El script imprime el resultado recuperado y validado. El procedimiento reproducible
sobre la captura está documentado arriba; la parte crítica es preservar el orden por
ID de transacción al reconstruir el túnel.

## Flag

```text
EVIL{d0t_tunnel1ng_r3ass3mbl3d_by_txid}
```

## Aprendizajes

- Un `SSLKEYLOGFILE` adjunto puede convertir una sesión TLS opaca en evidencia
  analizable.
- En túneles DNS, el orden de captura no sustituye el identificador de transacción:
  reensamblar por paquete corrompe el archivo transportado.
- Las consultas TXT cifradas pueden ocultar exfiltración incluso cuando el canal DNS
  viaja dentro de TLS.
