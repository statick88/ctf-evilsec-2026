# Circo beat

**Category**: Reversing  
**Difficulty**: Hard  
**Status**: solved and platform-validated

## Description

The challenge ships an old-looking HTML page with hundreds of randomized CSS classes and
colors. The visible page is a distraction: the useful data is in the color values.

## Solution

Each CSS `background-color: #RRGGBB` contributes three bytes. Reading every color in file
order as RGB bytes yields x86-64 Windows shellcode.

Disassembling the byte stream shows the shellcode resolving Windows APIs dynamically and
using CryptoAPI:

- `CryptAcquireContextA` with provider type `0x18` (`PROV_RSA_AES`)
- `CryptCreateHash` with `0x800c` (`CALG_SHA_256`)
- `CryptHashData` over the uppercased key string `FITO PAEZ`
- `CryptDeriveKey` with `0x6610` (`CALG_AES_256`)
- `CryptDecrypt` over a 48-byte blob
- `CreateFileA("flag.txt")` / `WriteFile`

The same result can be reproduced directly in Python: SHA-256 of `FITO PAEZ` is the
AES-256 key, the IV is all zeroes, and the encrypted blob starts at shellcode offset
`0x490` with length `0x30`.

```bash
python3 solve.py
```

## Flag

```text
EVIL{3l_4m0r_d3spu3s_d3l_c1fr4d0}
```

## Key takeaways

- A visual/random renderer may be a decoy; parse the static asset first.
- CSS color triples can be a byte stream.
- CryptoAPI constants in shellcode often reveal the exact derivation algorithm.
