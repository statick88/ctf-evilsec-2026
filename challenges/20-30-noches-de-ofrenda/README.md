# 30 noches de ofrenda

**Category**: Forensic  
**Difficulty**: Easy  
**Status**: solved and platform-validated

## Description

The Pombero legend text warns that the creature can be invisible. That points to
invisible Unicode rather than ordinary metadata or file carving.

## Solution

The visible text is ordinary UTF-8 Spanish, but the end of the file contains a long
sequence of zero-width characters:

- `U+200B ZERO WIDTH SPACE`
- `U+200C ZERO WIDTH NON-JOINER`

Mapping `U+200B` to bit `0` and `U+200C` to bit `1`, then grouping the bitstream in
8-bit bytes from offset 0, decodes directly to the flag.

```bash
python3 solve.py
```

## Flag

```text
EVIL{3l_s3cr3t0_d3l_p0mb3r0}
```

## Key takeaways

- Text forensics is not only metadata; invisible Unicode can carry a bitstream.
- The clue language (“invisible”) should be tested against Unicode categories before
  trying heavier tooling.
