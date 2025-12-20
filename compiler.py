import sys
from intelhex import IntelHex


# ---------------------------------------------------------
# Instruction table:
#   name: (operand_count, operand_type, opcode)
# operand_type:
#   0 = number
#   1 = register
#   2 = jump label
# ---------------------------------------------------------
INSTRUCTIONS = {
    "NOP": (0, 0, 0b00000_000),
    "MVA": (1, 0, 0b00001_001),
    "MOV": (2, 1, 0b00010_001),
    "ADD": (1, 0, 0b00100_001),
    "INC": (1, 1, 0b00101_001),
    "DEC": (1, 1, 0b00110_001),
    "SUB": (1, 0, 0b00111_001),
    "JMP": (1, 2, 0b01000_001),
    "JZE": (1, 2, 0b01001_001),
    "JZN": (1, 2, 0b01010_001),
    "JOF": (1, 2, 0b01011_001),
    "LDA": (1, 1, 0b01100_001),
    "STR": (1, 0, 0b01101_001),  # CPU internal use
    "LOD": (1, 0, 0b01110_001),  # CPU internal use
    "STA": (1, 1, 0b01111_001),
    "HLT": (0, 0, 0b11111_000)
}

REGISTERS = ["A", "B", "C", "D", "ACC"]


# ---------------------------------------------------------
# Convert byte list to Intel HEX
# ---------------------------------------------------------
def convert(data):
    ih = IntelHex()
    for addr, val in enumerate(data):
        ih[addr] = val
    ih.write_hex_file("program.hex")


# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------
def is_comment(line):
    return line.startswith("//")


def is_empty(line):
    return len(line.strip()) == 0


def parse_line_tokens(line):
    return line.split()


def is_label(line):
    return line.startswith(":") and len(line.split()) == 1


def valid_register(r):
    return r in REGISTERS

# ---------------------------------------------------------
# First pass: read file, extract labels and variables
# ---------------------------------------------------------
def first_pass(lines):
    labels = {}
    variables = {}
    address_counter = 0

    for i, line in enumerate(lines):
        line = line.strip()

        if is_empty(line) or is_comment(line):
            continue

        tokens = parse_line_tokens(line)

        # Variable definition
        if tokens[0] == "var":
            if len(tokens) != 3:
                raise SyntaxError(f"code.cpu:{i} -> Invalid variable definition: {line}")
            variables[tokens[1]] = tokens[2]
            continue

        # Label
        if is_label(line):
            label_name = line[1:]
            labels[label_name] = address_counter
            continue

        # Instruction size
        instr = tokens[0]
        if instr in ("HLT", "NOP"):
            address_counter += 1
        else:
            address_counter += 2

    return labels, variables


# ---------------------------------------------------------
# Operand resolution + type checking
# ---------------------------------------------------------
def resolve_operand(op, variables):
    """Replace variables with values."""
    if op in variables:
        return variables[op]
    return op


def validate_operand(instr, operand, expected_type, variables, line, line_num):
    operand = resolve_operand(operand, variables)

    if expected_type == 0:  # number
        if not operand.isdecimal():
            raise SyntaxError(f"code.cpu:{line_num} -> Expected number in '{line}'")
        return operand

    if expected_type == 1:  # register
        if valid_register(operand):
            return operand

        # Special STA/LDA handling for memory address
        if instr in ("LDA", "STA") and operand.isdecimal():
            return operand  # later converted to LOD/STR

        raise SyntaxError(f"code.cpu:{line_num} -> Expected register in '{line}'")

    return operand  # type 2 (label/number) checked later


# ---------------------------------------------------------
# Encode the instruction
# ---------------------------------------------------------
def encode_instruction(instr, ops, labels, line_num):
    opcode = INSTRUCTIONS[instr][2]

    # MOV: (reg, reg)
    if instr == "MOV":
        return [
            opcode,
            (REGISTERS.index(ops[0]) << 4) | (REGISTERS.index(ops[1]))
        ]

    # Register-only instructions
    if instr in ("LDA", "STA", "INC", "DEC"):
        return [opcode, REGISTERS.index(ops[0])]

    # Jumps
    if instr in ("JMP", "JZE", "JZN", "JOF"):
        op = ops[0]
        if not op.isdecimal():
            op = labels.get(op)
            if op is None:
                raise SyntaxError(f"code.cpu:{line_num} -> Unknown label '{ops[0]}'")
        return [opcode, int(op)]

    # Default: numeric operand
    if ops:
        return [opcode, int(ops[0])]

    return [opcode]


# ---------------------------------------------------------
# Second pass: encode instructions
# ---------------------------------------------------------
def second_pass(lines, labels, variables):
    output = []

    for i, line in enumerate(lines):
        line = line.strip()

        if is_empty(line) or is_comment(line) or is_label(line):
            continue

        tokens = parse_line_tokens(line)
        instruction = tokens.pop(0)

        # Variable declaration already handled
        if instruction == "var":
            continue

        if instruction not in INSTRUCTIONS:
            raise SyntaxError(f"code.cpu:{i} -> Unknown instruction '{instruction}'")

        expected_operands, expected_type = INSTRUCTIONS[instruction][:2]

        if len(tokens) < expected_operands or (len(tokens) > expected_operands and not tokens[expected_operands].startswith("//")):
            raise SyntaxError(
                f"code.cpu:{i} -> Expected {expected_operands} operands, got {len(tokens)} in '{line}'"
            )

        # Validate and resolve operands
        resolved_ops = []
        for op in tokens[:expected_operands]:
            resolved = validate_operand(instruction, op, expected_type, variables, line, i)
            resolved_ops.append(resolved)

        # Translate LDA/STA to LOD/STR when operand is numeric
        if instruction in ("LDA", "STA") and resolved_ops[0].isdecimal():
            instruction = "LOD" if instruction == "LDA" else "STR"

        encoded = encode_instruction(instruction, resolved_ops, labels, i)
        output.extend(encoded)

    return output


# ---------------------------------------------------------
# Main Assembly
# ---------------------------------------------------------
def assemble(file_path):
    with open(file_path) as f:
        lines = f.readlines()

    labels, variables = first_pass(lines)
    bytecode = second_pass(lines, labels, variables)

    print(bytecode)
    convert(bytecode)


if __name__ == "__main__":
    assemble(sys.argv[1])
