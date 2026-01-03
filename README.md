# Simulated CPU in Digital

**Author:** Daniel Huršan - 550273

---

## Description
This project was created as a final assignment in the PB170 course. The topic I chose was to design and implement a simulated CPU in Digital.

---

## 1. Architecture
The CPU has an 8-bit address and data space. It has access to four general-purpose registers, labeled A–D, and several special registers, such as the Instruction Register, Accumulator, Flag Register, and Program Counter. An EEPROM with an 8-bit address and data space is also connected to the CPU.

The CLK signal can be connected either to a clock component (currently set to 10 Hz) or to a simple button, which allows stepping through each clock cycle manually.

The system is composed of several blocks: `FETCH`, `DECODE`, `EXECUTE`, and `REGFILE`.

- `FETCH` → reads the address from the Program Counter and fetches the next byte from program memory  
- `DECODE` → decodes the instruction byte and determines the instruction and number of operands  
- `EXECUTE` → executes the instruction and prepares data for the `REGFILE`  
- `REGFILE` → manipulates the general-purpose registers and the accumulator  

---

## 2. Execution of an Instruction
The program memory is structured so that the first byte represents the instruction code and the following byte represents the operand, if the instruction has one. First, the instruction at the address stored in the Program Counter is fetched. The byte is decoded, where the upper 5 bits represent the instruction code and the lower 3 bits represent the number of operands. For example:

```
11100_001
Instruction -> 11100
Number of operands -> 1
```


After decoding, a counter is set based on the number of operands. If the instruction has one operand, the next byte in program memory is treated as an operand rather than as an instruction.

The execution flow of the CPU is as follows:

- PC → points to the instruction byte  
- CLK signal → the byte is decoded, stored in the Instruction Register, and the operand counter is set  

**If the number of operands is not 0:**  
- PC → points to the operand byte  
- CLK signal → the operand is processed and the instruction is executed  

This means that most instructions take two clock cycles to execute. The exceptions are `NOP` and `HLT`.

---

## 3. Instruction Table
The CPU currently supports 16 instructions:

| Instruction | Code_OperandsCount | Operands | Description |
|------------|--------------------|----------|-------------|
| NOP | 00000_000 | 0 | No operation |
| MVA | 00001_001 | 1 | Move value to accumulator |
| MOV | 00010_001 | 2 | Move data between registers |
| ADD | 00100_001 | 1 | Add operand to accumulator |
| INC | 00101_001 | 1 | Increment register |
| DEC | 00110_001 | 1 | Decrement register |
| SUB | 00111_001 | 1 | Subtract operand from accumulator |
| JMP | 01000_001 | 1 | Unconditional jump |
| JZE | 01001_001 | 1 | Jump if zero flag set |
| JZN | 01010_001 | 1 | Jump if zero flag not set |
| JOF | 01011_001 | 1 | Jump if overflow flag set |
| LDA | 01100_001 | 1 | Load accumulator from memory |
| STR | 01101_001 | 1 | Store accumulator to memory (internal use) |
| LOD | 01110_001 | 1 | Load accumulator from memory (internal use) |
| STA | 01111_001 | 1 | Store accumulator to memory |
| HLT | 11111_000 | 0 | Halt CPU execution |

**NOTE:**

**1.** The `MOV` instruction has two operands according to the table, because in the custom assembly language it uses two operands. However, the processor itself sees only one operand byte. The upper 4 bits represent the source register and the lower 4 bits represent the destination register. This is also why the *OperandsCount* and *Operands* columns do not match.

**2.** There are two instructions labeled as *internal use*: `STR` and `LOD`. These exist because the assembly language allows the user to specify both a register and a memory address for the `LDA` and `STA` instructions. The CPU needs a way to differentiate between an address byte and a register byte. These instructions are not intended to be used directly in user code; instead, `LDA` and `STA` should be used with both an address and a register.

---

## 4. Custom Assembly and Compiler
Digital supports loading a hex file into memory components. This makes it possible to write assembly code, compile it using a Python script, and run it on the simulated CPU. The script uses `.cpu` files. To invoke the compiler, use:

```
python3 compiler.py <your_file>.cpu
```


### 4.1. Assembly Syntax
Each instruction and its operands are written on a single line, separated by spaces:

```
ADD 1
```

To use a register as an operand, it is written as follows:

```
MOV A B
```

Comments are supported and can be created using the `//` prefix. Labels are also supported, allowing users to reference symbolic names instead of explicit addresses for jump instructions. Labels are defined using `:`, must not contain spaces, and must be placed on their own line:

```
:start // this is a comment, and this line defines the label 'start'
JMP start
```

Variables are supported as well. To initialize and use a variable, the syntax is:

```
var name_of_variable value
ADD name_of_variable
```


The value of a variable can be either a numeric value or a register.

---

### 4.2. Compiler
The compiler is a Python script that is executed on a `.cpu` file and generates a `program.hex` file, which can then be loaded into the ROM component of the CPU.

The compiler supports both syntax checking and type checking. Additionally, labels and variables can be defined after they are used, because the script processes the code in two passes: the first pass identifies labels and variables, and the second pass replaces them with their actual values and encodes the instructions and operands.

Digital specifically uses the Intel HEX format, which is why the compiler relies on the `IntelHex` library.

---

### 4.3. VS Code Extension

For ease of use, I created an extension you can install in Visual Studio Code via the `Extensions: Install from VSIX` command. This adds color support for `.cpu` files, keyboard shortcuts for commenting and even autofilling instructions. To get the full effect, the user needs to add:
```
"editor.tokenColorCustomizations": {
    "textMateRules": [
        {
            "scope": "label.cpu",
            "settings": {
                "foreground": "#e63e49"
            }
        },
        {
            "scope": "register.cpu",
            "settings": {
                "foreground": "#f3b256"
            }
        },
        {
            "scope": "var.cpu",
            "settings": {
                "foreground": "#8cf5db"
            }
        }
    ]
}
```
to their `settings.json` file.
---

## 5. Peripherals
Peripherals available in the Digital software can be connected to the CPU registers. As an example, a seven-segment display is connected to register D. Although the registers are only 8 bits wide, there is nothing preventing the user from combining two registers and connecting them to a peripheral.

---

## 6. Issues
The biggest challenges were related to the conceptual design. Determining how to select instructions, how they should be processed, and how data should be stored required significant effort. After creating a small prototype, development progressed much more smoothly. Having a base template for instruction implementation made adding new instructions easier.

Another recurring issue involved fixing timing errors after refactoring. Occasionally, signals were accidentally connected directly to output and not via a register or vice-versa, which disrupted the CPU timing. These issues were usually easy to fix but often took time to identify.

---

## 7. Future Work

### 7.1. Registers
The number of registers could be increased. Currently, registers use 3 bits for identification, but 4 bits could be used instead, allowing up to 16 registers including the accumulator. The 4-bit limitation exists because of how the `MOV` instruction is implemented. If multiple operand bytes were supported, all 8 bits could be used for register addressing.

### 7.2. Instructions
Currently I use 5 bits and only about half of the available instruction codes are used. The instruction encoding could also be expanded, since only 1 bit is required to represent the operand count (0 or 1). This would leave 7 bits available for the instruction code itself.

### 7.3. Operand Count
At the beginning of the project, I considered supporting two operands per instruction. With the current counter-based setup, this should be possible without completely rewiring the execution logic. However, the focus was ultimately placed on accumulator-based operations.
