import eval_fns


def extract_label_locs(statements):
    # Iterate through the statements, keeping track of the instruction address for each statement.
    # Also keep a dictionary of labels -> addresses.
    labels = {}
    address = 0
    for statement in statements:
        if statement["type"] == "instruction":
            address += 1
            continue
        elif statement["type"] == "directive":
            if statement["subtype"] == "label_def":
                # we are defining a label
                if statement["label"] in labels:
                    raise SyntaxError("Duplicate label %s!" % statement["label"])
                # label is new
                labels[statement["label"]] = address

    return labels


def assemble_statements(statements, labels):
    address = 0
    insnbits_arr = []
    for statement in statements:
        if statement["type"] is not "instruction":
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
