#!/usr/bin/env python3
# solve.py — Capybara Keygen: La Llave del Santuario (#10)
# .NET assembly keygen: decrypts flag via XOR with '*'

import dnfile

def main():
    d = dnfile.dnPE('CapybaraKeygen.dll')
    
    # Extract encrypted flag from static field with RVA
    for f in d.net.mdtables.FieldRva.rows:
        rva = f.Rva
        field_row = f.Field.row
        field_name = field_row.Name
        if field_name == 'C33F05E9445C44F8452D67F85FE572B688D227B5F91C68D8F88D3D76EC0CE961':
            offset = d.get_offset_from_rva(rva)
            encrypted = d.get_data(offset, 32)
            break
    
    # XOR key is '*' (0x2a) from XorKey literal field
    key = 0x2a
    decrypted = bytes([b ^ key for b in encrypted])
    # Flag ends at '}'
    flag_end = decrypted.find(b'}') + 1
    flag = decrypted[:flag_end].decode('utf-8')
    print(flag)

if __name__ == '__main__':
    main()
