#!/usr/bin/env python3
# solve.py — MateVM 1 (#1)
# Custom Rust VM license validator. Extracts bytecode, implements VM emulator.
# The flag is the valid license that produces "Acceso concedido."

import struct
import sys

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

class MateVM:
    """MateVM emulator based on bytecode structure."""
    
    def __init__(self, instructions):
        self.instructions = instructions
        self.pc = 0
        self.stack = []
        self.registers = [0] * 16  # r0-r15
        self.memory = bytearray(65536)
        self.flag = None
    
    def decode_instruction(self, inst):
        """Decode 13-byte instruction."""
        if inst is None or len(inst) < 13:
            return None
        return {
            'idx': inst[0],
            'opcode': inst[2],
            'a': inst[3],
            'b': inst[5],
            'c': inst[6],
            'd': inst[8],
            'e': inst[9],
            'result': inst[12]
        }
    
    def execute_instruction(self, inst_decoded):
        """Execute single instruction. Opcode semantics inferred from structure."""
        if inst_decoded is None:
            return False
        
        op = inst_decoded['opcode']
        a, b, c, d, e = inst_decoded['a'], inst_decoded['b'], inst_decoded['c'], inst_decoded['d'], inst_decoded['e']
        result = inst_decoded['result']
        
        # Opcode semantics (hypothetical, based on operand patterns):
        # 0x00: LOAD/MEMOP
        # 0x01: ARITH/LOGIC
        # 0x03: CMP/JMP
        # 0x06: STACKOP
        # 0x07: CHAR_VALIDATE
        
        # This is a placeholder - full semantics require interpreter analysis
        print(f"  PC={self.pc:2d} OP=0x{op:02x} A=0x{a:02x} B=0x{b:02x} C=0x{c:02x} D=0x{d:02x} E=0x{e:02x} RES=0x{result:02x}")
        return True
    
    def run(self, license_input):
        """Run VM with license input."""
        print(f"Running VM with license: {license_input}")
        self.pc = 0
        self.stack = list(license_input.encode())
        
        # Execute instructions in order
        for i, inst in enumerate(self.instructions):
            self.pc = i
            dec = self.decode_instruction(inst)
            if not self.execute_instruction(dec):
                break
        
        # Check result (placeholder)
        return False

def main():
    print("=== MateVM 1 - License Validator VM ===\n")
    
    bytecode = extract_bytecode()
    print(f"Bytecode region: 0x5488-0x5610 ({len(bytecode)} bytes)")
    
    header, instructions = parse_bytecode(bytecode)
    print(f"Header (14 bytes): {header.hex()}")
    print(f"  Decoded (-0x60): {bytes([(b-0x60)&0xFF for b in header]).hex()}")
    print(f"Instructions found: {len([i for i in instructions if i])}/22\n")
    
    # Print instruction table
    print("=== MateVM Instruction Set ===")
    print(f"{'Idx':>3} {'Opcode':>6} {'A':>4} {'B':>4} {'C':>4} {'D':>4} {'E':>4} {'Res':>4}")
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
    
    if instructions[1] is None:
        print("\n⚠ Instruction 1 is MISSING (logical index 1)")
        print("  Header byte 1 (decoded) = 0x01 - possible opcode for instr 1")
    
    # Key interpreter addresses
    print("\n=== Key Interpreter Addresses ===")
    print("  0x18ebf: Main VM loop (recursive)")
    print("  0x11b30: Print/error output")
    print("  0x12100: Helper function")
    print("  0x19ed0: License check orchestration")
    print("  0x1c200: Character classification (a-z)")
    print("  0x19704: VM runner")
    
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
        print(f'  "{s}"')
    
    # VM Emulator (incomplete - requires opcode semantics)
    print("\n=== VM Emulator ===")
    vm = MateVM(instructions)
    
    # The license must be lowercase a-z only (per character classification at 0x1c200)
    # Flag format: EVIL{...} but input is lowercase only
    # Hypothesis: license = "evil{...}" in lowercase
    
    # Try brute force on short licenses (not feasible for full flag)
    # Full solution requires implementing opcode semantics from 0x18ebf
    
    print("\n=== Flag Recovery ===")
    print("The VM validates a license key input character-by-character (a-z only).")
    print("The valid license producing 'Acceso concedido.' is the flag.")
    print("Format: EVIL{...}")
    print("\nCurrent status: VM structure documented, full emulation needed.")
    print("Opcode semantics must be derived from interpreter at 0x18ebf.")
    
    # For platform submission, we need the confirmed flag
    # This script documents the structure for manual/semi-automated completion
    return 1

if __name__ == '__main__':
    sys.exit(main())