from instructions import *

INSTRUCTION_TO_PARSE_FN = {
  "halt" : chgstat, 
  "exx" : chgstat, 
  "exf" : chgstat, 
  "ei" : chgstat, 
  "di" : chgstat, 
  "nop" : chgstat, 
  "add" : alu, 
  "sub" : alu, 
  "and" : alu, 
  "or" : alu, 
  "xor" : alu, 
  "cmp" : alu, 
  "lsl" : alu, 
  "lsr" : alu, 
  "adc" : alu, 
  "sbc" : alu, 
  "test" : alu, 
  "asr" : alu, 
  "vadd" : alu, 
  "vsub" : alu, 
  "vlsl" : alu, 
  "vlsr" : alu, 
  "iadd" : alu, 
  "isub" : alu, 
  "iand" : alu, 
  "ior" : alu, 
  "ixor" : alu, 
  "icmp" : alu, 
  "ilsl" : alu, 
  "ilsr" : alu, 
  "load" : load_store, 
  "in" : unimplemented, 
  "store" : load_store, 
  "out" : unimplemented, 
  "movl" : mov_hl, 
  "movh" : mov_hl, 
  "mov" : mov, 
  "int" : unimplemented, 
  "jmp" : jmp_call, 
  "call" : jmp_call, 
  "ret" : ret, 
  "jcc" : jmp_call, 
}

# Takes in a literal of the form "#1234" or "$89ab". 
# Literals starting with '#' are decimal.
# Literals starting with '$' are hex.
def parse_int_literal_string(literal):
  if literal.startswith("#"):
    return int(literal[1:])
  elif literal.startswith("$"):
    return int(literal[1:], 16)
  else:
    raise SyntaxError("Invalid literal syntax on token %s" % literal)


REGS = ["%ax", "%bx", "%cx", "%dx", "%bp", "%si", "%di", "%sp"]
CONDS = ["eq", "ne", "ge", "gt", "lt", "le", "cs", "cc"]

ALU_RR_ALU_OPBITS = {
  "add": 0b0000,
  "sub": 0b0001,
  "and": 0b0010,
  "or": 0b0011,
  "xor": 0b0100,
  "cmp": 0b0101,
  "lsl": 0b0110,
  "lsr": 0b0111,
  "adc": 0b1000,
  "sbc": 0b1001,
  "test": 0b1010,
  "asr": 0b1011,
  "vadd": 0b1100,
  "vsub": 0b1101,
  "vlsl": 0b1110,
  "vlsr": 0b1111,
}

ALU_RI_ALU_OPBITS = {
  "add" : 0b000,
  "sub" : 0b001,
  "and" : 0b010,
  "or"  : 0b011,
  "xor" : 0b100,
  "cmp" : 0b101,
  "lsl" : 0b110,
  "lsr" : 0b111
}

CHGSTAT_INSNBITS = {
  "halt": 0b000,
  "exx": 0b001,
  "exf": 0b010,
  "ei": 0b011,
  "di": 0b100,
  "nop": 0b111
}



