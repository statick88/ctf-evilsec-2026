#!/usr/bin/env python3
"""Analyze challenge 15: Ecos Ocultos: Ruido Controlado.

The PNG was cropped by changing the IHDR height from 430 to 350 while leaving
all IDAT scanlines and the original IHDR CRC in place.  The correct first step
is therefore to restore height 430 and unfilter every scanline with the PNG
standard algorithm.  Hidden rows and bitplanes are then checked without claiming
a flag unless one is actually present.
"""

from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

BINARY_FLAG = re.compile(rb"EVIL\{[^}\r\n]{1,128}\}")
INPUT = Path(__file__).with_name("ruido.png")
WIDTH = 625
VISIBLE_HEIGHT = 350
BYTES_PER_PIXEL = 3


def read_chunks(data: bytes) -> list[tuple[bytes, bytes, bytes]]:
    chunks: list[tuple[bytes, bytes, bytes]] = []
    pos = 8
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        crc = data[pos + 8 + length : pos + 12 + length]
        chunks.append((chunk_type, chunk_data, crc))
        pos += 12 + length
        if chunk_type == b"IEND":
            break
    return chunks


def paeth(left: int, up: int, up_left: int) -> int:
    p = left + up - up_left
    pa = abs(p - left)
    pb = abs(p - up)
    pc = abs(p - up_left)
    if pa <= pb and pa <= pc:
        return left
    if pb <= pc:
        return up
    return up_left


def unfilter_png_scanlines(raw: bytes, width: int, bpp: int) -> np.ndarray:
    stride = 1 + width * bpp
    if len(raw) % stride != 0:
        raise ValueError(f"raw IDAT length {len(raw)} is not a multiple of row stride {stride}")

    height = len(raw) // stride
    previous = bytearray(width * bpp)
    output = bytearray()
    filter_counts: dict[int, int] = {}

    for y in range(height):
        off = y * stride
        filter_type = raw[off]
        if filter_type not in range(5):
            raise ValueError(f"unsupported PNG filter {filter_type} at row {y}")
        filter_counts[filter_type] = filter_counts.get(filter_type, 0) + 1

        current = bytearray(raw[off + 1 : off + stride])
        for i, value in enumerate(current):
            left = current[i - bpp] if i >= bpp else 0
            up = previous[i]
            up_left = previous[i - bpp] if i >= bpp else 0

            if filter_type == 1:  # Sub
                current[i] = (value + left) & 0xFF
            elif filter_type == 2:  # Up
                current[i] = (value + up) & 0xFF
            elif filter_type == 3:  # Average
                current[i] = (value + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:  # Paeth
                current[i] = (value + paeth(left, up, up_left)) & 0xFF
            # filter_type 0 leaves the byte unchanged.

        output += current
        previous = current  # PNG predictors use the reconstructed prior row.

    print(f"Decoded {height} rows; filter counts: {filter_counts}")
    return np.frombuffer(bytes(output), dtype=np.uint8).reshape(height, width, bpp)


def extract_full_image(data: bytes) -> np.ndarray:
    chunks = read_chunks(data)
    idat = b"".join(chunk_data for chunk_type, chunk_data, _ in chunks if chunk_type == b"IDAT")
    raw = zlib.decompress(idat)
    return unfilter_png_scanlines(raw, WIDTH, BYTES_PER_PIXEL)


def restore_full_png(data: bytes, output_path: Path) -> Path:
    restored = bytearray(data)
    restored[20:24] = struct.pack(">I", 430)
    restored[29:33] = struct.pack(
        ">I", zlib.crc32(restored[12:16] + restored[16:29]) & 0xFFFFFFFF
    )
    output_path.write_bytes(restored)
    return output_path


def pack_bits(bits: np.ndarray, bitorder: str) -> bytes:
    usable = bits[: (bits.size // 8) * 8].astype(np.uint8)
    return np.packbits(usable, bitorder=bitorder).tobytes()


def search_blob(label: str, blob: bytes) -> str | None:
    match = BINARY_FLAG.search(blob)
    if match:
        return f"{label}: {match.group().decode()}"
    return None


def scan_direct_bitplanes(image: np.ndarray) -> str | None:
    regions = {
        "all": image,
        "visible": image[:VISIBLE_HEIGHT],
        "hidden": image[VISIBLE_HEIGHT:],
    }

    for region_name, region in regions.items():
        streams = {
            "R": region[:, :, 0],
            "G": region[:, :, 1],
            "B": region[:, :, 2],
            "RGB": region.reshape(region.shape[0], -1),
            "BGR": region[:, :, ::-1].reshape(region.shape[0], -1),
        }
        for stream_name, stream in streams.items():
            flat = stream.ravel()
            for plane in range(8):
                bits = (flat >> plane) & 1
                for bitorder in ("big", "little"):
                    blob = pack_bits(bits, bitorder)
                    result = search_blob(
                        f"{region_name} {stream_name} bit{plane} {bitorder}", blob
                    )
                    if result:
                        return result
    return None


def scan_common_multiplane_orders(image: np.ndarray) -> str | None:
    regions = {"all": image, "hidden": image[VISIBLE_HEIGHT:]}
    channel_orders = {"RGB": (0, 1, 2), "BGR": (2, 1, 0), "R": (0,), "G": (1,), "B": (2,)}
    plane_orders = {
        "lsb012": (0, 1, 2),
        "msb765": (7, 6, 5),
        "byte_lsb": tuple(range(8)),
        "byte_msb": tuple(reversed(range(8))),
    }

    for region_name, region in regions.items():
        for channel_name, channels in channel_orders.items():
            for plane_name, planes in plane_orders.items():
                bits: list[int] = []
                for row in region:
                    for pixel in row:
                        for channel in channels:
                            value = int(pixel[channel])
                            bits.extend((value >> plane) & 1 for plane in planes)
                bit_array = np.array(bits, dtype=np.uint8)
                for bitorder in ("big", "little"):
                    blob = pack_bits(bit_array, bitorder)
                    result = search_blob(
                        f"{region_name} {channel_name} {plane_name} {bitorder}", blob
                    )
                    if result:
                        return result
    return None


def solve() -> str:
    data = INPUT.read_bytes()
    original_height = struct.unpack(">I", data[20:24])[0]
    stored_crc = struct.unpack(">I", data[29:33])[0]

    restored_ihdr = bytearray(data[16:29])
    restored_ihdr[4:8] = struct.pack(">I", 430)
    restored_crc = zlib.crc32(b"IHDR" + restored_ihdr) & 0xFFFFFFFF
    print(f"IHDR height in file: {original_height}")
    print(f"Stored IHDR CRC: 0x{stored_crc:08x}; CRC if height=430: 0x{restored_crc:08x}")

    image = extract_full_image(data)
    Image.fromarray(image).save(Path(__file__).with_name("full_image.png"))
    restore_full_png(data, Path(__file__).with_name("ruido_fixed.png"))

    hidden = image[VISIBLE_HEIGHT:]
    print(f"Hidden rows: {hidden.shape[0]}; means={hidden.mean(axis=(0, 1))}; std={hidden.std(axis=(0, 1))}")

    for scanner in (scan_direct_bitplanes, scan_common_multiplane_orders):
        result = scanner(image)
        if result:
            return result

    return (
        "UNSOLVED: restored 430-row PNG and scanned direct/common bitplane orders; "
        "no flag-shaped token found. Continue with procedural-noise/seed analysis."
    )


if __name__ == "__main__":
    print(solve())
