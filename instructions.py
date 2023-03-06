from bitstring import BitArray
import re
import lookups

def _parse_alu_rr(toks):
  # Passed an instruction looking like
  #   ['ADD',  '%ax', '%bx']
  op = toks[0]
  opbits = BitArray(uint=0b00001, length=5)
  alu_opbits = BitArray(uint=lookups.ALU_RR_ALU_OPBITS[op], length=4)
  h = BitArray(uint=0, length=1) # TODO: Decide how h functionality will be used
  dst, src = toks[1], toks[2]
  dst, src = lookups.REGS.index(dst), lookups.REGS.index(src)
  dst, src = BitArray(uint=dst, length=3), BitArray(uint=src, length=3)
  return opbits + alu_opbits + h + src + dst

def _parse_alu_ri(toks):
  op = toks[0]
  opbits = BitArray(uint=0b00010, length=5)
  alu_opbits = BitArray(uint=lookups.ALU_RI_ALU_OPBITS[op], length=3)
  h = BitArray(uint=0, length=1) # TODO: Decide how h functionality will be used
  imm = lookups.parse_int_literal_string(toks[2])
  imm = BitArray(uint=imm, length=4)
  dst = toks[1]
  dst = lookups.REGS.index(dst)
  dst = BitArray(uint=dst, length=3)
  return opbits + alu_opbits + h + imm + dst

def alu(insn):
  toks = re.split(", |,| ", insn)
  if toks[-1].startswith("%"):
    return _parse_alu_rr(toks)
  else:
    return _parse_alu_ri(toks)

# MOVH and MOVL instrs.
def mov_hl(insn):
  # Passed an instruction looking like
  #   MOVL %ix, $FF
  toks = re.split(", |,| ", insn)
  op = toks[0]
  opbits = BitArray(uint=0b00111, length=5) if op == "movl" else BitArray(uint=0b01011, length=5)
  imm = lookups.parse_int_literal_string(toks[2])
  imm = BitArray(uint=imm, length=8)
  dst = lookups.REGS.index(toks[1])
  dst = BitArray(uint=dst, length=3)
  return opbits + imm + dst

# All load and store instrs:
# Base + Offset LOAD and STORE
# Pre-Indexed LOAD and STORE
# Post-Indexed LOAD and STORE
def _parse_base_offset(toks):
  # ex: STORE %ax, [%sp{, #8}]
  base_is_sp = False
  op = BitArray(uint=0b00100, length=5) if toks[0].startswith("load") else BitArray(uint=0b01000, length=5)
  w = BitArray(uint=0, length=1) if toks[0].endswith("b") else BitArray(uint=1, length=1)
  imm = 0
  if len(toks) == 4:
    # We actually have an offset
    imm = lookups.parse_int_literal_string(toks[3].strip(" ]"))
  src, trf = toks[2].strip("[ ]"), toks[1].strip(" ,")
  src, trf = lookups.REGS.index(src), lookups.REGS.index(trf)
  if src == 6: # if we're using %sp as the base, we have some extra room for imm
    imm = BitArray(int=imm, length=7)
    base_is_sp = True
  else:
    imm = BitArray(int=imm, length=4)
  src, trf = BitArray(uint=src, length=3), BitArray(uint=trf, length=3)

  if base_is_sp:
    op = BitArray(uint=0b00101, length=5) if toks[0].startswith("load") else BitArray(uint=0b01001, length=5)
    return op + w + imm + trf
  else:
    return op + w + imm + src + trf

def _parse_pre_index(toks):
  # ex: STORE %ax, [%ix, #8]!
  op = BitArray(uint=0b00110, length=5) if toks[0].startswith("load") else BitArray(uint=0b1010, length=5)
  h = BitArray(uint=0, length=1)
  w = 0 if toks[0].endswith("b") else 1
  w = BitArray(uint=w, length=1)
  imm5 = lookups.parse_int_literal_string(toks[3].strip(" ]!"))
  imm5 = BitArray(int=imm5, length=5)
  src, trf = toks[2].strip("[ "), toks[1].strip(" ,")
  src, trf = lookups.REGS.index(src), lookups.REGS.index(trf)
  if src != 4 and src != 6: # make sure src corresponds to %ix or %sp
    raise AssertionError("Source must be %ix for pre or post indexed load/store!")
  s = 0 if src == 4 else 1 # 0 for %ix, 1 for %sp
  s = BitArray(uint=s, length=1)
  src, trf = BitArray(uint=src, length=3), BitArray(uint=trf, length=3)
  return op + w + h + s + imm5 + trf
    
def _parse_post_index(toks):
  # ex: STORE %ax, [%ix], #8
  op = BitArray(uint=0b00110, length=5) if toks[0].startswith("load") else BitArray(uint=0b01010, length=5)
  h = BitArray(uint=1, length=1)
  w = 0 if toks[0].endswith("b") else 1
  w = BitArray(uint=w, length=1)
  imm5 = lookups.parse_int_literal_string(toks[-1])
  imm5 = BitArray(int=imm5, length=5)
  src, trf = toks[2].strip("[ ]"), toks[1].strip(" ,")
  src, trf = lookups.REGS.index(src), lookups.REGS.index(trf)
  if src != 4 and src != 6: # make sure src corresponds to %ix or %sp
    raise AssertionError("Source must be %ix for pre or post indexed load/store!")
  s = 0 if src == 4 else 1 # 0 for %ix, 1 for %sp
  s = BitArray(uint=s, length=1)
  src, trf = BitArray(uint=src, length=3), BitArray(uint=trf, length=3)
  return op + w + h + s + imm5 + trf

def load_store(insn):
  # LOAD, LDIX, LDXPRE, LDXPOST
  toks = re.split(", |,| ", insn)
  if insn.endswith('!'):
    return _parse_pre_index(toks)
  elif insn.endswith(']'):
    return _parse_base_offset(toks)
  else:
    return _parse_post_index(toks)

# All processor status change instructions
# HALT, EXX, EXF, EI, DI, NOP
def chgstat(insn):
  # ex: HALT
  op = BitArray(uint=0, length=5)
  secondary_bits = lookups.CHGSTAT_INSNBITS[insn.split(" ")[0]]
  secondary_bits = BitArray(uint=secondary_bits, length=3)
  extra = BitArray(uint=0, length=8)
  return op + secondary_bits + extra

# MOV instruction
def mov(insn):
  # MOV %ax, %bx
  toks = re.split(", |,| ", insn)
  opbits = BitArray(uint=0b01110, length=5)
  secondary_bits = BitArray(uint=0b000, length=3)
  hw = BitArray(uint=0, length=2) # TODO: Decide how hw functionality will be used
  dst, src = toks[1], toks[2]
  dst, src = lookups.REGS.index(dst), lookups.REGS.index(src)
  dst, src = BitArray(uint=dst, length=3), BitArray(uint=src, length=3)
  return opbits + secondary_bits + hw + src + dst

# All control-transfer instructions except RET (or RETI, if that gets implemented)
# JMP, JMPR, CALL, CALLR
def _parse_indirect_jc(toks):
  op = BitArray(uint=0b10001, length=5) if toks[0] == "jmp" else BitArray(uint=0b10011, length=5)
  padding = BitArray(uint=0b00000000, length=8)
  dst = toks[1]
  dst = lookups.REGS.index(dst)
  dst = BitArray(uint=dst, length=3)
  return op + padding + dst

def _parse_direct_jc(toks):
  op = BitArray(uint=0b10000, length=5) if toks[0] == "jmp" else BitArray(uint=0b10010, length=5)
  imm = int(toks[1])
  imm = BitArray(int=imm, length=11)
  return op + imm

def _parse_conditional_jump(toks):
  op = BitArray(uint=0b01101, length=5)
  cnd = toks[0].split('.')[1]
  cnd = lookups.CONDS.index(cnd)
  cnd = BitArray(uint=cnd, length=3)
  imm = int(toks[1])
  imm = BitArray(int=imm, length=8)
  return op + cnd + imm

def jmp_call(insn):
  toks = insn.split(" ")
  if toks[1].startswith("%"):
    # indirect jump or call (through register)
    return _parse_indirect_jc(toks)
  elif toks[0].startswith('j.'):
    # conditional jump
    return _parse_conditional_jump(toks)
  else:
    # direct jump or call (via offset)
    return _parse_direct_jc(toks)

# RET instruction. It's special. (not really)
def ret(insn):
  return BitArray(uint=0b0110000000000000, length=16)

def unimplemented(insn):
  raise NotImplementedError("Instruction %s isn't implemented!" % insn)