# cheesegrater

## Info

This is an assembler for the [pARMesan](https://github.com/Pritjam/parmesan) architecture. It takes input of SWISS assembly files (carrying the `.sws` extension) and creates WHEEL executable files from them. This repository also contains (or will eventually contain) the documentation for the WHEEL executable file format (a cheesy analog of the well-established ELF file format). 

Currently, the assembler also takes in `.wedge` files, which serve as chunks of data to be loaded into memory. This is a temporary measure, as eventually the .sws file format will support embedding data into it and/or a compiler will be written. A `.wedge` file is very simple. The first 2 bytes are the starting offset to load the data into, and the remaining bytes are the data.

## Usage

To compile a file, just invoke `python3 main.py INPUT OUTPUT`, where `INPUT` is the SWISS file to assemble, and `OUTPUT` is the path to write the WHEEL binary to. Run with the `-h` option to see a help message.

## WHEEL Format

The WHEEL format is intended to be a comprehensive binary format, somewhat similar to the ELF file format, but closer to a disk image binary. It contains several sections ("wedges") that are loaded into memory at different locations.

It starts with an 8-byte header. All values in this header are little-endian. The first 4 bytes of this header are a magic identifier that reads `whee`. The next byte is the version number (currently 1). The next byte is the number of memory wedges stored in this file (up to 256). The last two bytes are currently reserved.

Following this 8-byte header are a series of wedges, the amount specified in the file header. Each wedge starts with an 8-byte header. All values in this header are little-endian. The first 2 bytes of this header are the starting address to load the data into memory. The next 2 bytes are the length of data (not including the header). The last 4 bytes are currently reserved, but could eventually store a checksum or some other value.

## Code Examples

There are some sample SWISS files in the `sws` directory to help you get a feel for the pARMesan assembly format. For more information on pARMesan, check out the WIP [docs](https://github.com/Pritjam/pARMesan/blob/main/docs/index.md)