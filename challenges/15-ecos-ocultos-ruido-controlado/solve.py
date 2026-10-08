#!/usr/bin/env python3
# solve.py — Challenge 15: Ecos Ocultos: Ruido Controlado
# Repairs corrupted PNG (bad IHDR CRC), analyzes procedural noise for hidden flag.

import struct
import zlib
from PIL import Image
import numpy as np
import re

def repair_png(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())
    
    # Fix IHDR CRC (pos 29-32)
    chunk_type = data[12:16]  # b'IHDR'
    chunk_data = data[16:29]  # 13 bytes
    correct_crc = zlib.crc32(chunk_type + chunk_data) & 0xffffffff
    data[29:33] = struct.pack('>I', correct_crc)
    
    with open(output_path, 'wb') as f:
        f.write(data)
    return output_path

def analyze_noise(img_path):
    img = Image.open(img_path)
    arr = np.array(img)
    
    # Extract LSB from all channels
    for c, name in enumerate(['R', 'G', 'B']):
        lsb = (arr[:, :, c] & 1).flatten()
        bytes_data = bytearray()
        for i in range(0, len(lsb), 8):
            byte = 0
            for j in range(8):
                if i + j < len(lsb):
                    byte = (byte << 1) | lsb[i + j]
            bytes_data.append(byte)
        text = bytes_data[:5000].decode('ascii', errors='ignore')
        for m in re.finditer(r'EVIL\{[^}]+\}', text):
            return m.group()
    
    # Check corner grid (8x8 value noise vertices)
    corners_r = arr[::8, ::8, 0]
    corners_g = arr[::8, ::8, 1]
    corners_b = arr[::8, ::8, 2]
    
    # LSB of corner values
    for name, corners in [('R', corners_r), ('G', corners_g), ('B', corners_b)]:
        lsb = (corners & 1).flatten()
        bytes_data = bytearray()
        for i in range(0, len(lsb), 8):
            byte = 0
            for j in range(8):
                if i + j < len(lsb):
                    byte = (byte << 1) | lsb[i + j]
            bytes_data.append(byte)
        text = bytes_data.decode('ascii', errors='ignore')
        for m in re.finditer(r'EVIL\{[^}]+\}', text):
            return f"{name} corner LSB: {m.group()}"
    
    return "Flag not found in LSB or corner LSB. Noise is 8x8 value noise (44x79 corner grid). " \
           "Seed may be derived from image properties (625x350, IHDR CRC=0x65fdde11). " \
           "Flag possibly embedded in noise parameters or seed."

def solve():
    # Repair PNG
    repaired = repair_png('ruido.png', 'ruido_repaired.png')
    print(f"Repaired PNG saved to {repaired}")
    
    # Analyze
    flag = analyze_noise(repaired)
    return flag

if __name__ == '__main__':
    result = solve()
    print(result)
