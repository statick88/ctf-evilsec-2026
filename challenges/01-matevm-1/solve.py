#!/usr/bin/env python3
# solve.py — MateVM 1 (#1)
# Custom Rust VM license validator. Extracts bytecode, documents structure.
# Full VM emulation required to recover exact flag.

import struct

def extract_bytecode():
    with open('matevm', 'rb') as f:
        data = f.read()
    
    # Bytecode at file offset 0x5488, length 392 bytes
    bytecode = data[0x5488:0x5488+392]
    return bytecode

def parse_bytecode(bytecode):
    marker = b'tmvml'
    parts = bytecode.split(marker)
    header = parts[0]
    instructions = parts[1:]
    
    # Decode: subtract 0x60 from each byte
    decoded_insts = []
    for inst in instructions:
        dec = bytes([(b - 0x60) & 0xFF for b in inst])
        logical_idx = dec[0]
        decoded_insts.append((logical_idx, dec))
    
    # Reorder by logical index
    max_idx = max(d[0] for d in decoded_insts)
    reordered = [None] * (max_idx + 1)
    for logical_idx, inst in decoded_insts:
        reordered[logical_idx] = inst
    
    return header, reordered

def analyze_instructions(instructions):
    print("=== MateVM Instruction Set ===")
    print(f"{'Idx':>3} {'Opcode':>6} {'Op3':>4} {'Op5':>4} {'Op6':>4} {'Op8':>4} {'Op9':>4} {'Last':>4}")
    print("-" * 50)
    
    opcodes = {}
    for idx, inst in enumerate(instructions):
        if inst:
            opcode = inst[2]
            opcodes[opcode] = opcodes.get(opcode, 0) + 1
            print(f"{idx:3d}  0x{inst[2]:02x}     0x{inst[3]:02x}  0x{inst[5]:02x}  0x{inst[6]:02x}  0x{inst[8]:02x}  0x{inst[9]:02x}  0x{inst[12]:02x}")
        else:
            print(f"{idx:3d}  MISSING")
    
    print(f"\nOpcode distribution: {dict(sorted(opcodes.items()))}")
    
    # Missing instruction 1
    if instructions[1] is None:
        print("\n⚠ Instruction 1 is MISSING (logical index 1)")
        print("  Header byte 1 (decoded) = 0x01 - possible opcode for instr 1")

def main():
    print("=== MateVM 1 - License Validator VM ===\n")
    
    bytecode = extract_bytecode()
    print(f"Bytecode region: 0x5488-0x5610 ({len(bytecode)} bytes)")
    
    header, instructions = parse_bytecode(bytecode)
    print(f"Header (14 bytes): {header.hex()}")
    print(f"  ASCII: {header.decode(errors='ignore')}")
    print(f"  Decoded (-0x60): {bytes([(b-0x60)&0xFF for b in header]).hex()}")
    print(f"Instructions found: {len([i for i in instructions if i])}/22\n")
    
    analyze_instructions(instructions)
    
    # Interpreter locations
    print("\n=== Key Interpreter Addresses ===")
    print("  0x18ebf: Main VM loop (recursive)")
    print("  0x11b30: Print/error output")
    print("  0x12100: Helper function")
    print("  0x19ed0: License check orchestration")
    print("  0x1ec90: String formatting")
    print("  0x1eda0: Cleanup")
    print("  0x1ee70: Final VM entry")
    
    # Strings
    print("\n=== Relevant Strings ===")
    strings = [
        "=== MateVM License Checker ===",
        "Ingrese licencia: ",
        "Licencia inválida.",
        "Acceso concedido.",
        "EVIL",
    ]
    for s in strings:
        print(f"  \"{s}\"")
    
    # Flag hypothesis
    print("\n=== Flag Recovery ===")
    print("The VM validates a license key input character-by-character.")
    print("The valid license producing 'Acceso concedido.' is the flag.")
    print("Format: EVIL{...}")
    print("\nCurrent status: VM structure documented, full emulation needed.")
    print("Hypothesized flag based on context: EVIL{m4t3vm_l1c3ns3_v4l1d}")
    print("(Exact flag requires implementing VM semantics from 0x18ebf)")

if __name__ == '__main__':
    main()
