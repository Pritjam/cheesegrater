#!/usr/bin/env python3
from bitstring import BitArray
import sys
import os
import parse
import eval

WHEEL_VERSION = 1
PROCESSOR_START_ADDR = 0xF000

# Handle arguments
if "-h" in sys.argv:
    print(
        "Run with 2 arguments. Arg1 is the input file path, arg2 is the output file path."
    )
    exit(0)

if len(sys.argv) < 3:
    print(
        "Run with at least 2 arguments. Arg1 is the input file path, arg2 is the output file path. Additional args are memdump files to add."
    )
    exit(1)

in_path = sys.argv[1]
out_path = sys.argv[2]
if not os.path.exists(in_path):
    print("No such file exists for input file of:\n\t%s" % in_path)
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

mem_segments = []

if len(sys.argv) > 3:
    print("Parsing memdump(s)")
    for memdump_filename in sys.argv[3:]:
        with open(memdump_filename, "rb") as memdump_file:
            start_address = memdump_file.read(2)
            data = memdump_file.read()
            mem_segments.append({"start": start_address, "data": data})
    print(f"Read {len(mem_segments)} memory segments")


print("writing to file")

with open(out_path, "wb") as file:
    # Write WHEEL header
    #   char magic_identifier[4]; // should be "whee"
    #   uint8_t version;
    #   uint8_t num_of_segments;
    #   uint16_t reserved;
    file.write(b"whee")
    file.write(BitArray(uint=WHEEL_VERSION, length=8).bytes)
    file.write(BitArray(uint=len(mem_segments) + 1, length=8).bytes)
    file.write(BitArray(uint=0, length=16).bytes)

    # having written the header, now we write each segment, starting with the main code segment
    # format of each header:
    # uint16_t start_address;
    # uint16_t length;
    # uint32_t checksum; // currently unimplemented, but might eventually be
    file.write(
        BitArray(uintle=PROCESSOR_START_ADDR, length=16).bytes
    )  # start address is always 0xF000
    length = len(assembled) * 2
    file.write(BitArray(uintle=length, length=16).bytes)
    file.write(BitArray(uint=0, length=32).bytes)  # checksum
    for instr in assembled:
        instr.byteswap()
        file.write(instr.bytes)

    for memseg in mem_segments:
        file.write(memseg["start"])
        length = len(memseg["data"])
        file.write(BitArray(uintle=length, length=16).bytes)
        file.write(BitArray(uint=0, length=32).bytes)  # checksum
        file.write(memseg["data"])
