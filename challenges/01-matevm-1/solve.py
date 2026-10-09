#!/usr/bin/env python3
"""Recover the MateVM 1 license.

The Rust binary decrypts a compact bytecode program from .rodata, then runs a
simple one-byte VM against each input byte.  The program is easier to solve
statically than dynamically: each character is loaded, transformed by a few
8-bit operations, compared with a target byte, and asserted.
"""

from __future__ import annotations

from pathlib import Path

BINARY = Path(__file__).with_name("matevm")
PROGRAM_LEN = 0x18F
SRC_BASE = 0x5617
KEY_BASE = 0x5488
DIV3_MAGIC = 0xAAAAAAAAAAAAAAAB


def rol8(value: int, count: int) -> int:
    count &= 7
    return ((value << count) | (value >> (8 - count))) & 0xFF if count else value & 0xFF


def ror8(value: int, count: int) -> int:
    count &= 7
    return ((value >> count) | (value << (8 - count))) & 0xFF if count else value & 0xFF


def decrypt_program(data: bytes) -> list[int]:
    """Mirror the decryption loop at 0xff91..0xfff1."""

    out: list[int] = []
    rsi = 1
    rcx = 0

    while True:
        # The binary computes floor(rcx / 3) with a reciprocal multiply, rounds
        # it down to an even value, then multiplies by three. This skips the
        # literal `tmvml` separators embedded in the source stream.
        product = rcx * DIV3_MAGIC
        rdx = (product >> 64) >> 1
        rdx &= ~1
        rdx = rdx + rdx * 2
        source = SRC_BASE - rdx

        out.append(data[source + rsi - 1] ^ data[KEY_BASE + rsi - 1])
        if rsi == PROGRAM_LEN:
            break
        out.append(data[source + rsi] ^ data[KEY_BASE + rsi])

        rcx += 2
        rsi += 2

    return out


def execute_ops(initial: int, ops: list[tuple[int, int]]) -> int:
    value = initial
    for opcode, arg in ops:
        if opcode == 2:  # xor
            value ^= arg
        elif opcode == 3:  # add
            value = (value + arg) & 0xFF
        elif opcode == 4:  # sub
            value = (value - arg) & 0xFF
        elif opcode == 5:  # rol
            value = rol8(value, arg)
        elif opcode == 6:  # ror
            value = ror8(value, arg)
        else:
            raise ValueError(f"unsupported opcode {opcode:#x}")
    return value


def recover_flag(program: list[int]) -> str:
    instructions = [program[i : i + 3] for i in range(0, len(program), 3)]
    flag = ["?"] * 22
    pc = 0

    while pc < len(instructions):
        opcode, arg, _ = instructions[pc]
        if opcode == 9:  # end
            break
        if opcode != 1:  # load input[arg]
            raise ValueError(f"expected load at instruction {pc}, got {opcode:#x}")

        index = arg
        pc += 1
        ops: list[tuple[int, int]] = []

        while instructions[pc][0] != 7:  # compare accumulator with target
            ops.append((instructions[pc][0], instructions[pc][1]))
            pc += 1

        target = instructions[pc][1]
        pc += 1
        if instructions[pc][0] != 8:  # assert previous comparison succeeded
            raise ValueError(f"expected assertion at instruction {pc}")
        pc += 1

        matches = [chr(c) for c in range(0x20, 0x7F) if execute_ops(c, ops) == target]
        if len(matches) != 1:
            raise ValueError(f"ambiguous byte {index}: {matches}")
        flag[index] = matches[0]

    return "".join(flag)


def main() -> int:
    program = decrypt_program(BINARY.read_bytes())
    print(recover_flag(program))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
