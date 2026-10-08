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

def extract_full_image(input_path, output_path):
    """Reconstruct full 430x625 image from all IDAT data."""
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Extract all IDAT chunks
    pos = 8
    idat_data = b''
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        chunk_data = data[pos+8:pos+8+length]
        if chunk_type == b'IDAT':
            idat_data += chunk_data
        pos += 12 + length
        if chunk_type == b'IEND':
            break
    
    decompressed = bytearray(zlib.decompress(idat_data))
    
    # Reconstruct full image (430 rows x 625 cols x 3 channels)
    width = 625
    height = 430
    bytes_per_row = 1 + width * 3
    
    img_data = bytearray(height * width * 3)
    for y in range(height):
        row_start = y * bytes_per_row
        row_end = row_start + bytes_per_row
        if row_end <= len(decompressed):
            row = bytearray(decompressed[row_start:row_end])
            filter_byte = row[0]
            pixels = row[1:]
            # Apply PNG filter
            if filter_byte == 0:  # None
                pass
            elif filter_byte == 1:  # Sub
                for i in range(3, len(pixels)):
                    pixels[i] = (pixels[i] + pixels[i-3]) % 256
            elif filter_byte == 2:  # Up
                if y > 0:
                    prev_row_start = (y-1) * bytes_per_row
                    prev_row_end = prev_row_start + bytes_per_row
                    prev_row = bytearray(decompressed[prev_row_start:prev_row_end])
                    prev_pixels = prev_row[1:]
                    for i in range(len(pixels)):
                        pixels[i] = (pixels[i] + prev_pixels[i]) % 256
            elif filter_byte == 3:  # Average
                for i in range(len(pixels)):
                    left = pixels[i-3] if i >= 3 else 0
                    up = 0
                    if y > 0:
                        prev_row_start = (y-1) * bytes_per_row
                        prev_row_end = prev_row_start + bytes_per_row
                        prev_row = bytearray(decompressed[prev_row_start:prev_row_end])
                        up = prev_row[1+i]
                    pixels[i] = (pixels[i] + ((left + up) // 2)) % 256
            elif filter_byte == 4:  # Paeth
                for i in range(len(pixels)):
                    left = pixels[i-3] if i >= 3 else 0
                    up = 0
                    up_left = 0
                    if y > 0:
                        prev_row_start = (y-1) * bytes_per_row
                        prev_row_end = prev_row_start + bytes_per_row
                        prev_row = bytearray(decompressed[prev_row_start:prev_row_end])
                        up = prev_row[1+i]
                        if i >= 3:
                            up_left = prev_row[1+i-3]
                    p = left + up - up_left
                    pa = abs(p - left)
                    pb = abs(p - up)
                    pc = abs(p - up_left)
                    if pa <= pb and pa <= pc:
                        pred = left
                    elif pb <= pc:
                        pred = up
                    else:
                        pred = up_left
                    pixels[i] = (pixels[i] + pred) % 256
            img_data[y * width * 3 : (y+1) * width * 3] = pixels
    
    img = Image.frombytes('RGB', (width, height), bytes(img_data))
    img.save(output_path)
    return output_path

def analyze_noise(img_path):
    img = Image.open(img_path)
    arr = np.array(img)
    
    # Extract LSB from all channels
    for c, name in enumerate(['R', 'G', 'B']):
        lsb = (arr[:, :, c] & 1).flatten()
        bytes_data = bytearray()
        for i in range(0, len(lsb), 8):
            byte_val = 0
            for j in range(8):
                if i + j < len(lsb):
                    byte_val = (byte_val << 1) | lsb[i + j]
            bytes_data.append(byte_val)
        text = bytes_data[:50000].decode('ascii', errors='ignore')
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
            byte_val = 0
            for j in range(8):
                if i + j < len(lsb):
                    byte_val = (byte_val << 1) | lsb[i + j]
            bytes_data.append(byte_val)
        text = bytes_data.decode('ascii', errors='ignore')
        for m in re.finditer(r'EVIL\{[^}]+\}', text):
            return f"{name} corner LSB: {m.group()}"
    
    # Check extra rows (hidden 80 rows) specifically
    if arr.shape[0] > 350:
        extra_rows = arr[350:, :, :]
        for c, name in enumerate(['R', 'G', 'B']):
            lsb = (extra_rows[:, :, c] & 1).flatten()
            bytes_data = bytearray()
            for i in range(0, len(lsb), 8):
                byte_val = 0
                for j in range(8):
                    if i + j < len(lsb):
                        byte_val = (byte_val << 1) | lsb[i + j]
                bytes_data.append(byte_val)
            text = bytes_data.decode('ascii', errors='ignore')
            for m in re.finditer(r'EVIL\{[^}]+\}', text):
                return f"Extra rows {name} LSB: {m.group()}"
    
    return ("Flag not found in LSB or corner LSB. Noise is 8x8 value noise "
            "(corner grid). Seed may be derived from image properties "
            "(625x350/430, IHDR CRC=0x65fdde11/0x706fc708). "
            "Flag possibly embedded in noise parameters or seed.")

def solve():
    # Repair PNG
    repaired = repair_png('ruido.png', 'ruido_repaired.png')
    print(f"Repaired PNG saved to {repaired}")
    
    # Extract full image (430x625)
    full_img = extract_full_image('ruido.png', 'full_image.png')
    print(f"Full image (430x625) saved to {full_img}")
    
    # Analyze
    flag = analyze_noise(full_img)
    return flag

if __name__ == '__main__':
    result = solve()
    print(result)