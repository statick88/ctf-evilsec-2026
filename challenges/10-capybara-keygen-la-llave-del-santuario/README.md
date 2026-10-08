# 10. Capybara Keygen: La Llave del Santuario

**Category**: Reversing (REVERSING)  
**Difficulty**: EASY  
**Points**: 100  

## Description

> Alguien dejó caer el verificador de llaves del Santuario Capybara. Te entregamos el binario .NET: decompilalo, entiende cómo valida la llave y recuperá la flag que esconde.
>
> **Formato de flag:** `EVIL{...}`

## Reconnaissance

```bash
$ file CapybaraKeygen.dll
CapybaraKeygen.dll: PE32 executable for MS Windows 4.00 (console), Intel i386 Mono/.Net assembly, 3 sections

$ strings CapybaraKeygen.dll | grep -iE 'flag|key|xor|encrypt'
EncryptedFlag
DecodeFlag
XorKey
GetString
Encoding
C33F05E9445C44F8452D67F85FE572B688D227B5F91C68D8F88D3D76EC0CE961
```

## Analysis

The assembly contains:
- `EncryptedFlag` — static readonly field (initialized in `.cctor`)
- `XorKey` — static literal field with value `'*'` (0x2A)
- `C33F05E9...` — static readonly field with RVA pointing to encrypted data (32 bytes)
- `DecodeFlag()` — method that performs XOR decryption
- `Main()` — reads input, validates length (11 chars), compares against hardcoded key `"g0ph3r_capy"`, then calls `DecodeFlag()` and prints result

The encrypted flag data at RVA 0x10888 (file offset 0xC88):
```
6f 7c 63 66 51 4e 1a 5e 44 19 5e 75 1b 46 75 4e
19 49 1a 47 5a 1b 46 19 4e 57 00 00 00 00 00 00
```

XOR key: `'*'` = 0x2A

Decryption: `flag[i] = encrypted[i] ^ 0x2A`

## Exploitation / Recovery

```python
encrypted = bytes.fromhex('6f7c6366514e1a5e44195e751b46754e19491a475a1b46194e57')
key = 0x2a
flag = bytes([b ^ key for b in encrypted]).decode().split('}')[0] + '}'
# EVIL{d0tn3t_1l_d3c0mp1l3d}
```

## Flag

```
EVIL{d0tn3t_1l_d3c0mp1l3d}
```

## Key Takeaways

- .NET assemblies can be fully analyzed with `dnfile` (Python) without Mono/ILSpy
- Static fields with `FieldRva` store initialized data in the PE image
- Literal fields (`fdLiteral`) have values in the `Constant` metadata table
- Simple XOR encryption with single-byte key is trivial to reverse
