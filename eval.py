import eval_fns


def assemble_statements(statements, labels):
    address = 0
    insnbits_arr = []
    for statement in statements:
        if statement["type"] != "instruction":
            continue
        # print(statement)
        # print("Assembling instr: ", statement)
        # replace label with address of label in jumps
        if "branch_dest" in statement and statement["branch_dest"]["type"] == "LABEL":
            statement["branch_dest"]["dest"] = labels[statement["branch_dest"]["dest"]]

        statement["address"] = address
        # call lookup fn
        insnbits = eval_fns.INSTR_TYPE_TO_EVAL_FN[statement["instr_type"]](statement)
        insnbits_arr.append(insnbits)
        address += 1
    return insnbits_arr
