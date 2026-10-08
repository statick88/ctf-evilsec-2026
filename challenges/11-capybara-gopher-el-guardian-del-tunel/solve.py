#!/usr/bin/env python3
# solve.py — Capybara Gopher: El Guardián del Túnel (#11)
# Go binary: key check + XOR decryption of flag

def main():
    # From static analysis:
    # - Key validation: input must be "g0ph3r_capy" (11 bytes)
    # - Encrypted flag at offset 0x1663c0 (32 bytes)
    # - Decryption: XOR each byte with 0x5A
    
    with open('gopher', 'rb') as f:
        data = f.read()
    
    # Encrypted flag at offset 0x1663c0 (32 bytes)
    encrypted = data[0x1663c0:0x1663c0+32]
    key = 0x5A
    flag = bytes([b ^ key for b in encrypted])
    flag_end = flag.find(b'}') + 1
    print(flag[:flag_end].decode())

if __name__ == '__main__':
    main()
