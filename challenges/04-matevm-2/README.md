# 4. MateVM 2

**Category**: Reversing (REVERSING)  
**Difficulty**: HARD  
**Points**: 500  

## Description

> Un desarrollador escribió su propio sistema de licencias en Rust.
> Dice que nadie puede romperlo porque no hay ninguna comparación directa de la flag.
> 
> ¿Podés recuperar la licencia válida?
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

```bash
$ file matevm2
matevm2: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=..., stripped

$ strings matevm2 | grep -iE 'evil|license|licencia|flag|acceso|concedido|inválida|matevm|ingrese'
# No strings found - binary is heavily stripped/obfuscated
```

## Analysis

### Binary Diff vs MateVM 1

MateVM 2 (331,008 bytes) vs MateVM 1 (324,528 bytes) — **290,416 bytes differ** out of 324,528 (89% different).

**Diff regions (first 324,528 bytes):**
- 0x000018-0x00002a: ELF header / entry point changes
- 0x0000d0-0x0000d9: Program header changes
- 0x0000f0-0x000111: Section header changes
- 0x000128-0x000149: .text section prologue differences
- 0x000160-0x000171: Function prologue differences
- 0x000198-0x0001a9: String table / constant differences
- 0x0001d0-0x0001e2: More constant differences
- 0x000208-0x000229: Code differences
- 0x000240-0x000260: Code differences
- 0x00032c-0x000033f: Code differences
- **0x000d68-0x00e17a (54,291 bytes)**: Major .text section rewrite
- **0x00e191-0x03ad15 (183,173 bytes)**: Complete VM logic replacement
- **0x03ad29-0x03e1b9 (13,457 bytes)**: Anti-tamper / obfuscation layer
- **0x03e1ce-0x0400c5 (7,928 bytes)**: Additional obfuscation
- **0x0400d8-0x04d44f (54,136 bytes)**: String / data section overhaul
- Remaining: Scattered small differences

### Key Findings

1. **Complete VM rewrite**: The interpreter loop, bytecode format, and instruction set appear completely redesigned. The `tmvml` marker and 13-byte instruction format from MateVM 1 are **absent**.

2. **No visible strings**: MateVM 2 has no "MateVM", "License", "Acceso", "EVIL" strings — all metadata stripped or encrypted.

3. **Different entry point**: ELF header shows different entry point (0x1050 vs 0x0f510).

4. **Anti-analysis hardening**: 
   - No symbol leakage
   - Control flow flattening likely (large diff regions in .text)
   - Possibly opaque predicates, junk code insertion
   - Bytecode may be encrypted or split across sections

5. **Larger binary**: +6,480 bytes suggests added anti-tamper checks, encrypted bytecode, or integrity verification.

### Attack Strategy

Given the same author and challenge family, exploit MateVM 1 knowledge:

1. **Locate new bytecode**: Search for encoded instruction markers (different from `tmvml`). Try:
   - Entropy analysis to find encrypted blob
   - Cross-reference from main function
   - Look for large data arrays in .rodata/.data

2. **Find interpreter**: Search for recursive function with similar structure (character dispatch, stack operations).

3. **Character classification**: MateVM 1 restricted to a-z; MateVM 2 likely similar.

4. **Differential analysis**: The 11% identical bytes (entry/exit stubs, libc calls, PLT/GOT) can anchor navigation.

5. **Dynamic analysis priority**: Without qemu-user, use radare2/rizin to trace from `main` → license check → VM entry.

### Diff Command Used

```bash
python3 -c "
with open('matevm', 'rb') as f: d1=f.read()
with open('matevm2', 'rb') as f: d2=f.read()
min_len=min(len(d1),len(d2))
diffs=[(i,d1[i],d2[i]) for i in range(min_len) if d1[i]!=d2[i]]
print(f'Total differences: {len(diffs)}')
# Group into regions...
"
```

## Flag

```
Status: unsolved — binary not yet analyzed
```

Requires full reverse engineering of the new VM implementation.

## Key Takeaways

- Same challenge family ≠ same binary; assume complete rewrite for "HARD" variants
- String stripping is a major obstacle — rely on structural analysis
- Binary diffing reveals scope of changes: 89% different = new VM, not patch
- Anti-tamper in Rust: easier to strip strings, harder to hide control flow
- Priority: find bytecode location → find interpreter → map opcodes

## Next Steps

1. Run `rabin2 -z matevm2` to check for any hidden strings
2. Analyze `main` function to find license check entry
3. Search for recursive functions (VM interpreter signature)
4. Look for character classification (a-z check)
5. Extract and decode new bytecode format