# 1. MateVM 1

**Category**: Reversing (REVERSING)  
**Difficulty**: MEDIUM  
**Points**: 300  

## Description

> Un desarrollador escribió su propio sistema de licencias en Rust.
> Dice que nadie puede romperlo porque no hay ninguna comparación directa de la flag.
>
> ¿Podés recuperar la licencia válida?
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

```bash
$ file matevm
matevm: ELF 64-bit LSB pie executable, x86-64, dynamically linked, stripped

$ strings matevm | grep -iE 'matevm|licencia|acceso|EVIL|tmvml'
=== MateVM License Checker ===
Ingrese licencia:
Licencia inválida.
Acceso concedido.
EVIL
```

The useful static anchor is not a direct flag comparison. It is the VM program material in
`.rodata`, around file offsets `0x5488` and `0x5617`, plus the interpreter code around
virtual address `0xff50`.

## Analysis

The earlier 13-byte logical-instruction model was a false lead. The real check decrypts a
399-byte bytecode stream and then interprets fixed **3-byte** instructions:

```text
[opcode, operand, padding]
```

The binary first verifies the candidate shape:

- length is `0x16` (22 bytes),
- first four bytes are `EVIL`,
- byte 4 is `{`,
- byte 21 is `}`.

Then it decrypts the bytecode with a repeating key stream beginning at `0x5488` (`latg...`) and
a source stream beginning at `0x5617`. The decryption loop also skips the embedded `tmvml`
separators via the reciprocal-multiply division-by-3 pattern.

The VM opcodes used by this challenge are:

| Opcode | Meaning |
|---|---|
| `1` | load candidate byte at `operand` |
| `2` | xor accumulator with `operand` |
| `3` | add `operand` modulo 256 |
| `4` | subtract `operand` modulo 256 |
| `5` | rotate accumulator left by `operand` bits |
| `6` | rotate accumulator right by `operand` bits |
| `7` | compare accumulator with `operand` |
| `8` | assert previous comparison |
| `9` | end program |

The bytecode is therefore a set of independent per-character constraints. For each loaded
candidate byte, brute-forcing printable ASCII through the short transform chain yields exactly
one match.

## Exploitation / Recovery

Run the solver:

```bash
$ python3 solve.py
EVIL{RUST_VM_BYT3C0D3}
```

The flag was submitted to the official EvilSec platform with:

```bash
python3 scripts/lib/ctf_platform.py claim 1 'EVIL{RUST_VM_BYT3C0D3}'
```

and the platform returned `correct`.

## Flag

```text
EVIL{RUST_VM_BYT3C0D3}
```

## Key Takeaways

- Rust metadata is noisy; focus on compact data references and the actual branch to success.
- The visible `tmvml` separators were a storage artifact, not instruction boundaries.
- Once the real 3-byte VM was mapped, the check reduced to independent byte constraints.
