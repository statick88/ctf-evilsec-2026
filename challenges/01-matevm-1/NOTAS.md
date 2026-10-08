# Notas de reconocimiento — Reto #1 MateVM 1

Documento de traspaso para quien retome este reto. Todo lo que sigue está **verificado**
en esta sesión; lo que sea hipótesis va marcado como tal.

## 1. Entorno: el bloqueo que frenó a los intentos anteriores

**Este host es aarch64 (ARM64). Todos los binarios del CTF son x86-64.** Por eso los
análisis anteriores se quedaron en estática pura: el binario no se podía ejecutar.

Preparación hecha y **verificada funcional**:

```console
$ sudo dpkg --add-architecture amd64
$ sudo apt-get update -qq
$ sudo apt-get install -y --no-install-recommends libc6:amd64
$ ls /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2     # el intérprete x86-64
$ cp challenges/01-matevm-1/matevm /tmp/opencode/ctf/   # el repo está en un mount FUSE
$ chmod +x /tmp/opencode/ctf/matevm
$ printf '' | qemu-x86_64 -L / /tmp/opencode/ctf/matevm
=== MateVM License Checker ===
Ingrese licencia: Licencia inválida.
```

Dos detalles que costaron tiempo y hay que respetar:

- **`qemu-user-static` NO está instalado; `qemu-user` sí**, y aporta `qemu-x86_64`
  (dinámico). Por eso hace falta el flag `-L /` para que encuentre la libc x86-64.
- **El repo está en `/mnt/hgfs`, un mount FUSE de VMware sin permiso de ejecución.**
  Si ejecutas el binario desde ahí, el shell lo interpreta como script y falla con
  errores absurdos (`ELF: not found`, `cannot create ... Directory nonexistent`).
  Hay que copiarlo a `/tmp` primero. No es un binario corrupto.

## 2. Comportamiento observado

Pide una licencia por stdin y responde `Licencia inválida.` Ante probé: cadena vacía,
1, 4 y 80 caracteres, `a-z` repetido, mayúsculas+dígitos, y tres formatos con guiones
(`aaaa-aaaa-...`, `1234-5678-...`, `matevm-0000-...`). **Todas rechazadas**, sin mensaje
de longitud ni de charset: el programa no filtra la entrada antes de validar, o el
filtro no es lo que parece.

## 3. Estructura del bytecode (la parte importante)

El programa de la VM vive en `.rodata` como **cadenas imprimibles**, no como bytes crudos.
Cada carácter codifica un byte: **`byte_real = char - 0x60`**.

- El marcador de inicio de cada bloque es la cadena `tmvml`, que decodifica a
  `14 0d 16 0d 0c`.
- Tras el marcador vienen instrucciones de **3 bytes** cada una.

Ejemplo verificado (`tmvmlita/mhctcumj`):

| codificada | decodificada | instrucciones |
|---|---|---|
| `tmvmlita/mhctcumj` | `14 0d 16 0d 0c` `09 14 01` `cf 0d 08` `03 14 03` `15 0d 0a` | 4 |

Los opcodes observados son `0x14` y `0x0d` en el **segundo** byte de cada instrucción.
**Faltan los índices `0x01` y `0x02`**: los primeros bytes de bloque que existen son
`00, 03, 04, 05, 06, 07, 08, 09, 0a, 0b, 0c, 0d, 0e, 0f, 10, 11, 12, 13, 14, 15`.
Con 22 entradas posibles (0x00..0x15) y 20 presentes, faltan exactamente dos.

### Hipótesis central (sin verificar)

El enunciado dice *"Dice que nadie puede romperlo porque no hay ninguna comparación
directa de la flag"*. Combinado con que faltan `0x01` y `0x02`, la hipótesis más
probable es que **se borraron instrucciones del programa y hay que reconstruirlas**,
o que `0x01`/`0x02` son opcodes que el intérprete rechaza por no estar implementados
y el programa solo funciona si caen en una ruta concreta. **Esto es conjetura**: hay que
confirmarlo leyendo el `switch` de dispatch del intérprete.

## 4. Contradicción entre intentos anteriores (no dar por bueno ninguno)

Dos análisis previos chocan; verifícalo tú antes de construir sobre ello:

| afirmación | fuente | estado |
|---|---|---|
| "13 bytes por instrucción, constantes 0x14/0x0d en posiciones fijas" | intento 1 | **parcialmente falso**: son 3 bytes, no 13 |
| "bytecode en offset 0x5488, 392 bytes, delimitado por `tmvml`" | intento 2 | **no verificado**; hay ~20 bloques `tmvml` separados, no uno de 392 bytes |
| "intérprete recursivo en 0x18ebf, dispatch sobre chars L,W,M,N,B,C,I,X,Y" | intento 2 | **no verificado** |
| "cabecera con contador de instrucciones 0x17 (23)" | intento 1 | **no verificado** |
| "instrucción 1 ausente, opcode 0x01" | intento 1 | **coincide** con el hueco 0x01/0x02 que sí verifiqué |

## 5. Rutas de ataque sugeridas, por orden de coste

1. **Instrumentar con `qemu-x86_64 -d` / `-strace`** para ver qué pasa con entradas de
   distinta longitud: si hay `read` con tamaño fijo, la longitud de la licencia está
   fijada ahí y eso acota el espacio de búsqueda.
2. **Localizar el intérprete y su `switch`**: buscar comparaciones contra `0x14` y `0x0d`
   en `.text` (`cmp $0x14`, `cmp $0x0d`) y seguir el dispatch. De ahí sale la tabla de
   opcodes real, que es el núcleo del writeup.
3. **Emular el programa en Python** con la tabla de opcodes: extraer los bloques `tmvml`,
   decodificar, y ejecutar. Si el programa es aritmética pura sobre la entrada, se
   resuelve invirtiendo las operaciones.
4. Solo si lo anterior no basta: parchear el binario con `unicorn` (ya instalado) para
   forzar la rama de éxito y volcar lo que el programa imprimiría.

## 6. Estado

`flag.txt` **no existe** para este reto y no debe crearse hasta que la plataforma
devuelva `correct`:

```console
$ cd /mnt/hgfs/statick/security/ctf/1
$ python3 scripts/lib/ctf_platform.py submit 1 'EVIL{...}'
$ python3 scripts/lib/ctf_platform.py claim 1 'EVIL{...}'    # solo si es correct
```

El candidato `EVIL{m4t3vm_l1c3ns3_v4l1d}` que circula en el README actual **nunca se
envió a la plataforma** y es una conjetura léxica derivada del nombre del reto.
Trátalo como basura, no como hipótesis.