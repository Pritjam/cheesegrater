# pARMesan Documentation

## Assembly Symbols

This ISA uses Intel syntax, meaning the first operand in a two-operand instruction is the Destination while the second one is the source. This is also the syntax used in RISC-V and A64. For example, the instruction SUB %ax, %bx will perform the computation %ax - %bx and store the result in %ax.

In this ISA, many operands of assembly instructions involve memory or registers. The syntax for these are listed below. In these syntaxes, curly braces `{}` indicate an optional element, while parentheses `()` indicate a required element. Square brackets `[]` do not have a semantic function--if they appear in syntax, that means they are part of the syntax. The vertical pipe `|` indicates a choice between two or more options.

### Register Operands
`<R(d|s|t)>` indicates a register operand. The letter used helps identify the purpose of that operand. `d` indicates a destination register, while `s` indicates a source register. `t` indicates a “transfer” register, which is the register to be transferred to/from in a memory operation.

### Immediates
`#imm` indicates an integer literal. The specification for the instruction in which this operand appears details exactly how many bits the operand is allowed. Integer literals can be written starting with a pound symbol `#`, in which case they are interpreted in decimal, or they can be written starting with a dollar sign `$`, in which case they are interpreted in hexadecimal. For example, the literals `#10` and `$a` are equivalent. Hexadecimal literals can be capitalized or in lowercase.

### Memory Operands
Memory operands are specified as `[mem]`. There are 3 forms this memory operand can take:
- Base + Offset: `[(%ix | %sp){, #imm}]`
- Pre-Indexed: `[<Rs>, #imm]!`
- Post-Indexed: `[<Rs>], #imm`

Note that only `%ix` or `%sp` can be used as the base register in Base + Offset addressing.

### Labels
Labels (jump targets) are denoted by an identifier, such as `.END`, `loop1`, or `.Branch4`. Labels must start with either a period or a letter (uppercase or lowercase). To define a label, write its identifier followed by a colon, such as `.END:`. Labels are case-sensitive, so `end` and `End` are two different labels.

## Assembler Directives

We support a few assembler directives to allow programmers (and eventually, compilers) to produce more flexible and complex code. These directives are modeled after the GNU ARM Assembler's directives.

- `.ascii <"string">` : inserts the string as data, without a null terminator
- `.asciiz <"string">`: inserts the string as data, with a null terminator
- `.align <boundary> {<fill_value>}` : aligns successive symbols on a boundary of `<boundary>` bytes. If provided, the 1-byte `<fill_value>` (specified as a numerical immediate, truncated to 1 byte if necessary) is used to pad up to the alignment boundary. A default value of `#0` is used if no fill value is provided.
- `.byte <val1> {, <val2>...}` : inserts one or more bytes in sequence at the current location. Each byte is specified as a numerical immediate, truncated to 1 byte if necessary.
- `.word <val1> {, <val2>...}` : inserts one or more 16-bit words in sequence at the current location. Each word is specified as a numerical immediate, truncated to 2 bytes if necessary. Each word is inserted in little-endian byte order.
- `.seek <address>` : The assembly code immediately following this directive will be written starting at the memory address provided. Functionally, this will be implemented as a seek() call during assembly. This allows for the specification of the exact location for things like the Interrupt Vector Table.

---

[Table of Contents](index.md)
