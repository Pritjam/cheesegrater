# cheesegrater

## Info

This is an assembler for the [pARMesan](https://github.com/Pritjam/parmesan) architecture. It takes input of SWISS assembly files (carrying the `.sws` extension) and creates WHEEL executable files from them. This repository also contains (or will eventually contain) the documentation for the WHEEL executable file format (a cheesy analog of the well-established ELF file format). 

## Usage

To compile a file, just invoke `python3 grater.py FILENAME.sws`. A WHEEL binary called `FILENAME` will be generated in the same directory. Optionally, you can specify the directory to store the WHEEL files with `python3 grater.py FILENAME.sws output_directory`. Run with the `-h` option to see a help message.