# 11. Capybara Gopher: El Guardián del Túnel

**Category**: Reversing (REVERSING)  
**Difficulty**: EASY  
**Points**: 150  

## Description

> El gopher capybara custodia un secreto dentro de un binario de Go. El programa pide una clave y, con la correcta, revela la flag — pero la flag no está en texto plano. Analizá el ejecutable y recuperala.
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

```bash
$ file gopher
gopher: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, BuildID[sha1]=c67e588d71975c9403daa0d313cd8572013639fc, with debug_info, not stripped

$ strings gopher | grep -iE 'clave|correcto|incorrecto|flag|evil'
Clave incorrecta.
Correcto! Flag:
EVIL
```

## Analysis

Using `go tool objdump` on the stripped-but-with-debug_info Go binary:

**Key validation** (`main.main`):
- Reads input from stdin (or argv[1])
- Checks length == 11 bytes
- Compares against hardcoded key: `"g0ph3r_capy"` (little-endian immediate values in instructions)
  - `MOVQ $0x635f723368703067` → `"g0ph3r_c"`
  - `CMPW $0x7061` → `"ap"`
  - `CMPB $0x79` → `"y"`

**Flag decryption** (inline in `main.main`):
- On correct key, loads encrypted flag from `main.encryptedFlag` (32 bytes at offset 0x1663c0)
- Decrypts via XOR with 0x5A per byte:
  ```asm
  MOVZX byte [rbx + rax], SI    ; load encrypted byte
  XORL $0x5a, SI                ; XOR with 0x5A
  MOVB SI, [rax + rbx]          ; store decrypted
  ```

Encrypted flag (32 bytes at file offset 0x1663c0):
```
6f 7c 63 66 51 4e 1a 5e 44 19 5e 75 1b 46 75 4e
19 49 1a 47 5a 1b 46 19 4e 57 00 00 00 00 00 00
```

## Exploitation / Recovery

```python
encrypted = bytes.fromhex('6f7c6366514e1a5e44195e751b46754e19491a475a1b46194e57')
key = 0x5A
flag = bytes([b ^ key for b in encrypted]).split(b'}')[0] + b'}'
# EVIL{g0_b1n4ry_r3v3rs3d}
```

Key: `g0ph3r_capy`

## Flag

```
EVIL{g0_b1n4ry_r3v3rs3d}
```

## Key Takeaways

- Go binaries with debug_info retain function names (`main.main`, `main.encryptedFlag`)
- `go tool objdump` is excellent for Go binary analysis
- Hardcoded string comparisons use immediate values in little-endian
- Simple XOR decryption inline in the validation logic
- Statically linked Go binaries are large but fully analyzable
