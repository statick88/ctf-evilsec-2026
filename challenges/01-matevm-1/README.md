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
matevm: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=27ec4d9755aabc3d3e932f22df3d22e7976a3d5d, stripped

$ strings matevm | grep -iE 'evil|license|licencia|flag|acceso|concedido|inválida'
=== MateVM License Checker ===
Ingrese licencia: 
Licencia inválida.
Acceso concedido.
EVIL
```

## Analysis

### VM Bytecode Structure

The binary contains a custom bytecode VM implemented in Rust. The bytecode is stored in the `.rodata` section at file offset `0x5488` (virtual address `0x485488`), spanning 392 bytes.

**Format:**
```
Header (14 bytes): "latg" + 0x17 (count=23) + "mkdtg" + 4 bytes
22 Instructions: each = "tmvml" (5 bytes) + 13 bytes data = 18 bytes
Total: 14 + 22×18 = 392 bytes
```

Each instruction (after `-0x60` decoding) is 13 bytes with fixed format:
| Byte | Value | Purpose |
|------|-------|---------|
| 0    | 0x00-0x15 | Logical instruction index |
| 1    | 0x14 | Constant delimiter |
| 2    | 0x00-0x07 | **Opcode** |
| 3    | var | Operand A |
| 4    | 0x0d | Constant delimiter |
| 5    | var | Operand B |
| 6    | var | Operand C |
| 7    | 0x14 | Constant delimiter |
| 8    | var | Operand D |
| 9    | var | Operand E |
| 10   | 0x0d | Constant delimiter |
| 11   | 0x0a | Constant delimiter |
| 12   | var | Checksum / result |

### Instruction Set (Logical Order)

| Idx | Opcode | Operands (3,5,6,8,9) | Last |
|-----|--------|----------------------|------|
| 0   | 0x06   | 0x23,0x0b,0x04,0x03,0x12 | 0x64 |
| 1   | **MISSING** | — | — |
| 2   | 0x06   | 0x06,0x0b,0x00,0x07,0xcf | 0xb6 |
| 3   | 0x03   | 0x13,0x08,0x06,0x03,0x12 | 0xd3 |
| 4   | 0x01   | 0xd3,0x08,0x02,0x01,0x2b | 0xaa |
| 5   | 0x07   | 0x95,0x0f,0x21,0x00,0x10 | 0x07 |
| 6   | 0x07   | 0x5f,0x09,0xe7,0x03,0x13 | 0x62 |
| 7   | 0x01   | 0x48,0x08,0x07,0x03,0x10 | 0xb6 |
| 8   | 0x07   | 0x3f,0x09,0xac,0x00,0x12 | 0x95 |
| 9   | 0x01   | 0xcf,0x08,0x03,0x03,0x15 | 0x3c |
| 10  | 0x07   | 0xaa,0x0b,0x06,0x03,0x12 | 0xe7 |
| 11  | 0x07   | 0xa0,0x0b,0x04,0x00,0x11 | 0x81 |
| 12  | 0x00   | 0x13,0x0b,0x06,0x07,0x75 | 0xf2 |
| 13  | 0x00   | 0x13,0x09,0x29,0x00,0x13 | 0xa1 |
| 14  | 0x03   | 0x10,0x0f,0x46,0x03,0x12 | 0xa8 |
| 15  | 0x06   | 0x42,0x0e,0x20,0x07,0x52 | 0x4b |
| 16  | 0x00   | 0x10,0x08,0x07,0x03,0x15 | 0x87 |
| 17  | 0x00   | 0x14,0x08,0x03,0x07,0x66 | 0x82 |
| 18  | 0x00   | 0x11,0x08,0x05,0x06,0xcd | 0xbc |
| 19  | 0x03   | 0x12,0x09,0x9d,0x03,0x10 | 0x9c |
| 20  | 0x03   | 0x12,0x09,0x3a,0x06,0xc4 | 0xef |
| 21  | 0x01   | 0x04,0x0f,0xf7,0x03,0x12 | 0xb0 |

**Opcode distribution:** 0x00×5, 0x01×4, 0x03×4, 0x06×3, 0x07×5

### VM Interpreter

The main interpreter loop is at `0x18ebf` (function `fcn.00018ebf`). Key characteristics:
- Recursive entry point (calls itself at `0x18ff5`)
- Processes instructions from a bytecode buffer
- Uses stack-based architecture with registers `rbx`, `r12`-`r15`
- Character classification checks for `'L'`, `'W'`, `'M'`, `'B'`, `'C'`, `'I'`, `'X'`, `'Y'`
- Calls `0x11b30` for output/error reporting
- Input read via `fgets` into stack buffer

### License Check Orchestration

Function at `0x19ed0` (`fcn.00019ed0`) orchestrates the license validation:
- Reads input character by character
- Validates each character via `0x1c200` (character classification: lowercase a-z only)
- Feeds characters to VM interpreter
- Prints "Acceso concedido." on success, "Licencia inválida." on failure

### Character Classification

Function at `0x1c200` maps input characters:
- Adds `0x9f` to input byte, compares to `0x19`
- Valid range: lowercase `'a'`-`'z'` (0x61-0x7a)
- Jump table at `0x24679` with 25 entries (8 bytes each) for each letter

### Missing Instruction #1

Logical index 1 absent from bytecode stream. Header at `0x5488` decodes to `0c 01 14 07 b7...` — byte `0x01` at offset 1 suggests opcode `0x01` for instruction 1.

### Key Interpreter Addresses

- `0x18ebf`: Main VM loop (recursive)
- `0x11b30`: Print/error function
- `0x12100`: Helper function
- `0x19ed0`: License check orchestration
- `0x1c200`: Character classification
- `0x19704`: VM runner (calls interpreter)

## Exploitation / Recovery

The VM validates a license key character-by-character (lowercase a-z only). The valid license that produces "Acceso concedido." is the flag.

**Recovery approach:**
1. Extract bytecode (offset `0x5488`, 392 bytes)
2. Parse 22 instructions (logical 0-21, #1 missing)
3. Implement VM semantics by analyzing interpreter at `0x18ebf`
4. Model stack/register operations for each opcode
5. Solve constraints to find input producing "Acceso concedido"

## Flag

```
Status: unsolved — VM emulator incomplete
```

The exact flag requires full VM emulation. The bytecode structure and interpreter locations are documented above for future completion.

## Key Takeaways

- Custom VMs in Rust binaries can be identified by recursive interpreter loops and bytecode data sections
- Instruction formats with fixed delimiters (0x14, 0x0d, 0x0a) indicate encoded bytecode
- radare2's `aaa` analysis + `pdf` on interpreter reveals semantics
- Rust binaries leak rich string metadata even when stripped (`panic` messages, format strings)
- Missing bytecode instructions may reside in header/adjacent data
- License validation VMs often check input character-by-character via state machine

## References

- radare2 book: https://radare.gitbook.io/radare2/
- Rust reversing: https://github.com/rust-reversing/rust-reversing