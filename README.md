# cheesegrater

## Info

This is an assembler for the [pARMesan](https://github.com/Pritjam/parmesan) architecture. It takes input of SWISS assembly files (carrying the `.sws` extension) and creates PARM executable files from them. PARM files are just a sequence of pARMesan instructions in a file, with a little metadata. This is in contrast to a more powerful file format, such as ELF. This repository also contains (or will eventually contain) the documentation for the WHEEL executable file format (a cheesy analog of the well-established ELF file format). 

## Usage

To compile a file, just invoke `python3 grater.py FILENAME.sws`. A WHEEL binary called `FILENAME` will be generated in the same directory. Optionally, you can specify the directory to store the WHEEL files with `python3 grater.py FILENAME.sws output_directory`. Run with the `-h` option to see a help message.

## Code Examples

There are some sample SWISS files in the `sws` directory to help you get a feel for the pARMesan assembly format. For more information on pARMesan, check out the WIP [docs](https://github.com/Pritjam/pARMesan/blob/main/docs/index.md)