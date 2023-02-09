import sys
import lookups
from instructions import jmp_call
from bitstring import CreationError, BitArray
import os.path
import re

input_path = sys.argv[1]

out_folder = sys.argv[2] if len(sys.argv) >= 3 else ""

if '-h' in sys.argv:
  print("""Run with -h for help.
To assemble a SWISS assembly file, run `python3 grater.py FILENAME.sws`. 
An output directory can also be specified, as `python3 grater.py FILENAME.sws output_directory`.""")
  exit(0)

# class ctx:
#   def __init__(self) -> None:
#     self.line = ""
#     self.label_dict = None
#     self.line_number = 0



code_lines = []
label_locations = {}
with open(input_path) as file:
  index = 0
  for line in file:
    line = line.split(";")[0]
    line = line.strip()
    
    # skip empty lines
    if line == "":
      continue

    # Labels
    match = re.search(r'(\.\w+):$', line)
    if match:
      label_locations[match.groups()[0]] = index
      continue
    
    # array lines
    match = re.search(r'da \[(.*)\]', line)
    if match:
      # now to determine if it's a well-formed array or not
      contents = match.groups()[0]
      contents = re.split(r',\s*', contents)
      for element in contents:
        try:
          elem = lookups.parse_int_literal_string(element)
        except SyntaxError as exception:
          print("Error! Bad syntax on array element %s" % elem)
          quit(0)
        if int(elem) > 2 ** 16 - 1:
          print("Error! Array element '%s' out of range!" % elem)
          quit(0)
        code_lines.append("dw %s" % elem)
        index += 1
      continue
    
      
    # Line of code or data
    code_lines.append(line)
    index += 1

# print("Lines of code found: ", code_lines)
# print("Labels and corresponding addresses found: ", label_locations)
# print("Registered all labels. Parsing instructions into bytes now")

# Now to actually assemble
instructions = []
for (index, code_line) in enumerate(code_lines):
  # print("Now processing line %s" % code_line)
  toks = code_line.split(" ")
  op = toks[0].lower()
  if op == 'dw':
    num = int(toks[1])
    instructions.append(BitArray(uint=num, length=16))
    continue
  if op.startswith("j."):
    op = "jcc"
  parser_fnc = lookups.INSTRUCTION_TO_PARSE_FN[op]

  line_lower = code_line.lower()

  if parser_fnc == jmp_call and toks[1] in label_locations:
    # this is a jump pointing to a valid label, meaning we must replace it with the offset
    line_lower = code_line.replace(toks[1], str(label_locations[toks[1]] - index)).lower()
  try:
    instructions.append(parser_fnc(line_lower))
  except CreationError as exception:
    print("Error parsing instruction %d: %s. \n\t%s" % (index, code_line, str(exception.msg)))
    exit(0)
  # except Exception as exception:
  #   print("Other error occurred: \n\t%s" % str(exception))
  #   exit(0)
    



# print("All instructions parsed. Writing to file %s now" % "out.pj")
# print(instructions)
filename = os.path.basename(input_path)
(filename, ext) = os.path.splitext(filename)
out_filename = os.path.join(out_folder, filename)
with open(out_filename, "wb") as file:
  for instr in instructions:
    file.write(instr.bytes)

      