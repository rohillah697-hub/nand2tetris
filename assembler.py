#!/usr/bin/env python3
"""
Hack Assembler (Nand to Tetris, project 06) - Capstone version.

Usage:
    python3 assembler.py Prog.asm            -> writes Prog.hack next to it
    python3 assembler.py Prog.asm Out.hack   -> writes Out.hack

How it works (two readings of the file):
  1. First reading: remove comments and blank lines, and remember the
     ROM address of every label like (LOOP).
  2. Second reading: turn every A- and C-instruction into 16 bits.
     A new variable gets the next free RAM address: 16, 17, 18, ...

Extra feature for my K = 61 (61 mod 3 = 1):
  For a wrong line the assembler prints a clear message with the line
  number, e.g. "Line 7: invalid instruction 'D=Q+1'", instead of crashing.
  All errors in the file are reported, and no .hack file is written.
"""

import sys

# ---------------------------------------------------------------- tables

COMP = {
    # a = 0 (uses A)
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "!D":  "0001101",
    "!A":  "0110001", "-D":  "0001111", "-A":  "0110011",
    "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    # a = 1 (uses M)
    "M":   "1110000", "!M":  "1110001", "-M":  "1110011",
    "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101",
}

JUMP = {
    "":    "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
for _i in range(16):
    PREDEFINED["R%d" % _i] = _i

SYMBOL_CHARS = set("abcdefghijklmnopqrstuvwxyz"
                   "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                   "0123456789_.$:")


class AsmError(Exception):
    """A problem in one line of the .asm file."""

    def __init__(self, line_no, message):
        super().__init__("Line %d: %s" % (line_no, message))


# ---------------------------------------------------------------- helpers

def clean(line):
    """Remove the comment and all spaces from one line."""
    line = line.split("//", 1)[0]
    return "".join(line.split())


def is_symbol(name):
    """A symbol is letters, digits, _ . $ : and does not start with a digit."""
    return (name != "" and not name[0].isdigit()
            and all(ch in SYMBOL_CHARS for ch in name))


def dest_bits(dest, line_no, text):
    """dest can be any of A, D, M in any order, each at most once."""
    if dest == "":
        return "000"
    if any(ch not in "ADM" for ch in dest) or len(set(dest)) != len(dest):
        raise AsmError(line_no, "invalid instruction '%s' (unknown destination '%s')"
                       % (text, dest))
    return ("1" if "A" in dest else "0") + \
           ("1" if "D" in dest else "0") + \
           ("1" if "M" in dest else "0")


def c_instruction(text, line_no):
    """Turn 'dest=comp;jump' into 16 bits."""
    dest, comp, jump = "", text, ""
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if comp not in COMP:
        raise AsmError(line_no, "invalid instruction '%s' (unknown computation '%s')"
                       % (text, comp))
    if jump not in JUMP:
        raise AsmError(line_no, "invalid instruction '%s' (unknown jump '%s')"
                       % (text, jump))
    return "111" + COMP[comp] + dest_bits(dest, line_no, text) + JUMP[jump]


# ---------------------------------------------------------------- passes

def first_pass(lines, errors):
    """Return the list of (line_no, instruction) and the label table."""
    symbols = dict(PREDEFINED)
    program = []
    for line_no, raw in enumerate(lines, start=1):
        text = clean(raw)
        if text == "":
            continue
        if text.startswith("("):
            if not text.endswith(")") or not is_symbol(text[1:-1]):
                errors.append(str(AsmError(line_no, "invalid label '%s'" % text)))
                continue
            symbols[text[1:-1]] = len(program)   # address of the next instruction
        else:
            program.append((line_no, text))
    return program, symbols


def second_pass(program, symbols, errors):
    """Translate every instruction into a 16-bit string."""
    out = []
    next_var = 16
    for line_no, text in program:
        try:
            if text.startswith("@"):
                value = text[1:]
                if value.isdigit():
                    number = int(value)
                    if number > 32767:
                        raise AsmError(line_no, "number too large in '%s' (max 32767)" % text)
                elif is_symbol(value):
                    if value not in symbols:
                        symbols[value] = next_var
                        next_var += 1
                    number = symbols[value]
                else:
                    raise AsmError(line_no, "invalid A-instruction '%s'" % text)
                out.append(format(number, "016b"))
            else:
                out.append(c_instruction(text, line_no))
        except AsmError as e:
            errors.append(str(e))
    return out


def assemble(source_text):
    """Return (list of 16-bit lines, list of error messages)."""
    errors = []
    program, symbols = first_pass(source_text.splitlines(), errors)
    binary = second_pass(program, symbols, errors)
    errors.sort(key=lambda m: int(m.split()[1].rstrip(":")))   # in line order
    return binary, errors


# ---------------------------------------------------------------- main

def main(argv):
    if len(argv) not in (2, 3) or not argv[1].endswith(".asm"):
        print("Usage: python3 assembler.py Prog.asm [Out.hack]")
        return 2
    in_path = argv[1]
    out_path = argv[2] if len(argv) == 3 else in_path[:-4] + ".hack"
    try:
        with open(in_path) as f:
            source = f.read()
    except OSError as e:
        print("Cannot open %s: %s" % (in_path, e.strerror))
        return 1

    binary, errors = assemble(source)
    if errors:
        for message in errors:
            print(message)
        print("%d error(s) found, %s was not written." % (len(errors), out_path))
        return 1

    with open(out_path, "w") as f:
        f.write("\n".join(binary) + "\n")
    print("Wrote %d instructions to %s" % (len(binary), out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
