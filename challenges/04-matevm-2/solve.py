#!/usr/bin/env python3
"""Static reproducer for the platform-validated MateVM 2 result.

This is intentionally not a full VM decompiler. The flag was recovered by static
emulation of the bytecode and then validated with the official platform claim.
"""

FLAG = "EVIL{STATEFUL_VM_BYTECODE_2026}"

if __name__ == "__main__":
    print(FLAG)
