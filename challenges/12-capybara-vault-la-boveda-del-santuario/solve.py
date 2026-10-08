#!/usr/bin/env python3
# solve.py — Capybara Vault: La Bóveda del Santuario (#12)
# ELF64 PIE stripped: key validation via arithmetic/XOR loop

def main():
    # From static analysis (radare2):
    # - Key length must be 18 bytes (0x12)
    # - Expected values at 0x2020 (18 bytes):
    #   ce ca d7 9d d9 ca db e5 eb 2d de 1a 09 c1 12 02 04 fe
    # - Validation per byte i (0-17):
    #   expected[i] = (key[i] + 1 + 3*i) ^ (0xAA - i)
    # - Solving for key:
    #   key[i] = (expected[i] ^ (0xAA - i)) - 1 - 3*i  (mod 256)
    
    expected = [0xce, 0xca, 0xd7, 0x9d, 0xd9, 0xca, 0xdb, 0xe5,
                0xeb, 0x2d, 0xde, 0x1a, 0x09, 0xc1, 0x12, 0x02, 0x04, 0xfe]
    
    key = bytearray(18)
    for i, exp in enumerate(expected):
        val = (exp ^ (0xAA - i)) - 1 - 3*i
        key[i] = val & 0xFF
    
    flag = b'EVIL{' + key + b'}'
    print(flag.decode())

if __name__ == '__main__':
    main()
