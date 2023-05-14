#!/usr/bin/env python3
from bitstring import BitArray
import sys
import os
import parse
import eval

VERSION = 6


# Handle arguments
if "-h" in sys.argv:
    print("Run with 2 arguments. Arg1 is the input file path, arg2 is the output file path.")
    exit(0)

if len(sys.argv) != 3:
    print("Run with excactly 2 arguments. Arg1 is the input file path, arg2 is the output file path.")
    exit(1)

in_path = sys.argv[1]
out_path = sys.argv[2]
if not os.path.exists(in_path):
    print("No such file exists for input file of:\n\t%s" % in_path)
    exit(1)

if not os.path.exists(os.path.dirname(out_path)):
    print("Nonexistent directory for output file of:\n\t%s" % out_path)
    exit(1)

print("parsing")
statements = []
# 1. Parse file, list of statements
with open(in_path, "r") as infile:
    for line in infile:
        parsed = parse.parse_line(line.strip().upper())
        if parsed is None:
            continue
        statements.append(parsed)
        # print("\t", parsed)

# 2. Evaluate file
#   a. Loop over once to determine offsets of each label
labels = eval.extract_label_locs(statements)

#   b. Loop over a second time, this time evaluating each instruction.
#      This step emits instructions to be written to the file.

print("assembling")
assembled = eval.assemble_statements(statements, labels)

print("writing to file")

with open(out_path, "wb") as file:
  # Write header
  #   char magic_identifier[4]; // should be "parm"
  #   uint16_t length;
  #   uint8_t version; 
  #   uint8_t reserved; // for future use
  file.write(b'parm')
  length = len(assembled) * 2
  file.write(BitArray(uintle=length, length=16).bytes)
  file.write(BitArray(uint=VERSION, length=8).bytes)
  file.write(b'\0')
  for instr in assembled:
    instr.byteswap()
    file.write(instr.bytes)

# instr.byteswap()
# file.write(instr.bytes)