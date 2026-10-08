# 12. Capybara Vault: La Bóveda del Santuario

**Category**: Reversing (REVERSING)  
**Difficulty**: MEDIUM  
**Points**: 250  

## Description

> La bóveda del Santuario Capybara valida una clave secreta antes de soltar su contenido. Te damos el binario (ELF de 64 bits, stripped): entendé su lógica de validación, recuperá la clave correcta y obtené la flag.
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

```bash
$ file vault
vault: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=b8fd2edb009368ff3ed9f0c244e2c248469335cf, for GNU/Linux 3.2.0, stripped

$ strings vault
EVIL
Acceso denegado.
%s%s}
```

## Analysis

Using radare2 (`r2 -A vault`):

**Main function** (`main` at 0x10e0):
- If argc > 1: uses argv[1] as key
- If argc == 1: reads from stdin via fgets
- Validates key length == 18 (0x12)
- Compares each byte against expected values at address 0x2020 (18 bytes)
- On success: prints flag using format `"EVIL{%s}"`
- On failure: prints `"Acceso denegado."`

**Validation loop** (addresses 0x1130-0x114d):
For each byte i (0-17):
```asm
movzx edx, byte [rbx + rax]    ; key[i]
mov esi, edi                   ; edi = -86 (0xFFFFFFFA)
sub esi, eax                   ; esi = -86 - i
add edx, ecx                   ; edx = key[i] + (1 + 3*i)
xor edx, esi                   ; edx = (key[i] + 1 + 3*i) ^ (-86 - i)
cmp dl, byte [r8 + rax]        ; compare with expected[i]
je continue_loop
```

Where:
- `ecx` starts at 1, increments by 3 each iteration → `1 + 3*i`
- `edi` = -86 (0xFFFFFFFA), `sub esi, eax` → `-86 - i`
- Only lower 8 bits matter for XOR → `(0xAA - i)` (since -86 ≡ 0xAA mod 256)
- Expected values at 0x2020: `ce ca d7 9d d9 ca db e5 eb 2d de 1a 09 c1 12 02 04 fe`

**Formula**: `expected[i] = (key[i] + 1 + 3*i) ^ (0xAA - i)`

**Solving for key**: `key[i] = (expected[i] ^ (0xAA - i)) - 1 - 3*i (mod 256)`

## Exploitation / Recovery

```python
expected = [0xce, 0xca, 0xd7, 0x9d, 0xd9, 0xca, 0xdb, 0xe5,
            0xeb, 0x2d, 0xde, 0x1a, 0x09, 0xc1, 0x12, 0x02, 0x04, 0xfe]

key = bytearray(18)
for i, exp in enumerate(expected):
    val = (exp ^ (0xAA - i)) - 1 - 3*i
    key[i] = val & 0xFF
# key = b'c_x0r_l00p_cr4ckm3'
flag = b'EVIL{' + key + b'}'
```

## Flag

```
EVIL{c_x0r_l00p_cr4ckm3}
```

## Key Takeaways

- Stripped PIE binaries still reveal logic via radare2 function analysis
- Validation loops with arithmetic/XOR can be reversed algebraically
- Constants in memory (0x2020) hold expected values — extract with `px`
- radare2's visual mode and `pdf` are powerful for understanding control flow
- Key validation without branching on individual bytes suggests algorithmic generation
