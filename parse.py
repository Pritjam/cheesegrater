import lex
import parse_lookups


def expect(condition, error, error_str):
    if not condition:
        raise error(error_str)


def parse_mem_operand(lexer: lex.lexer):
    mem_operand = {}
    expect(
        lexer.curr_tok.type == "LBRACKET",
        SyntaxError,
        "Expected memory operand to start with Left Bracket",
    )
    lexer.advance()
    expect(
        lexer.curr_tok.type == "REGISTER",
        SyntaxError,
        "Expected Register operand, instead found %s" % lexer.curr_tok.val,
    )
    mem_operand["source"] = lexer.curr_tok.val
    mem_operand["type"] = "base-offset"
    mem_operand["offset"] = 0
    lexer.advance()
    if lexer.curr_tok.type == "COMMA":
        lexer.advance()
        expect(
            lexer.curr_tok.type == "NUMBER",
            SyntaxError,
            "Expected Integer Literal operand, instead found %s" % lexer.curr_tok.val,
        )
        mem_operand["offset"] = lexer.curr_tok.val
        lexer.advance()
    expect(
        lexer.curr_tok.type == "RBRACKET",
        SyntaxError,
        "Unexpected token %s, expected Right Bracket" % lexer.curr_tok.val,
    )
    lexer.advance()
    if lexer.curr_tok.type == "COMMA":
        # post-index
        mem_operand["type"] = "post-index"
        lexer.advance()
        if lexer.curr_tok.type == "NUMBER":
            if mem_operand["offset"] != 0:
                raise SyntaxError(
                    "Cannot have both an immediate offset and a post-index offset"
                )
            mem_operand["offset"] = lexer.curr_tok.val
            lexer.advance()
        else:
            raise SyntaxError(
                "Expected Integer Literal operand, instead found %s"
                % lexer.curr_tok.val
            )
    elif lexer.curr_tok.type == "BANG":
        # pre-index
        mem_operand["type"] = "pre-index"
        lexer.advance()
    return mem_operand


def parse_instr_statement(lexer: lex.lexer):
    # print("Parsing instruction statement `%s`" % lexer.input_str)
    statement = {}
    statement["type"] = "instruction"
    # first token is the instruction opcode string
    statement["opcode"] = lexer.curr_tok.val
    # print("found instruction with opcode of %s" % statement["opcode"])
    # consume opcode token
    lexer.advance()

    # parse NOARG instrs
    if statement["opcode"] in parse_lookups.NO_ARG_INSTRS_LOOKUP:
        statement["instr_type"] = "noarg"
        pass

    # parse conditional jumps
    elif statement["opcode"] == "J":
        statement["instr_type"] = "jcc"
        # we should be looking at a PERIOD token right now
        expect(
            lexer.curr_tok.type == "PERIOD",
            SyntaxError,
            "Expected period after J opcode",
        )
        lexer.advance()
        expect(
            lexer.curr_tok.type == "STRING",
            SyntaxError,
            "Expected condition code following period in J.cc instruction",
        )
        statement["condition_code"] = lexer.curr_tok.val
        lexer.advance()
        # Looking for one label
        lexer.advance()
        expect(
            lexer.curr_tok.type == "STRING",
            SyntaxError,
            "Expected a label after J.cc instruction, found %s-type instead"
            % lexer.curr_tok.type,
        )
        statement["branch_dest"] = {"type": "LABEL", "dest": lexer.curr_tok.val}
        lexer.advance()

    # parse unconditional jumps, calls
    elif statement["opcode"] == "JMP" or statement["opcode"] == "CALL":
        statement["instr_type"] = "jump_call"
        # We might have a register, we might have a label
        if lexer.curr_tok.type == "REGISTER":
            statement["branch_dest"] = {"type": "REGISTER", "dest": lexer.curr_tok.val}
        elif lexer.curr_tok.type == "PERIOD":
            lexer.advance()
            expect(lexer.curr_tok.type == "STRING", SyntaxError, "Bad label for jump!")
            statement["branch_dest"] = {"type": "LABEL", "dest": lexer.curr_tok.val}
        else:
            raise SyntaxError(
                "Expected label or register for jump target, found %s-type instead"
                % lexer.curr_tok.type
            )
        lexer.advance()

    # parse loads and stores
    elif statement["opcode"] in ["LOADB", "STOREB", "LOADW", "STOREW"]:
        statement["instr_type"] = "load_store"
        expect(
            lexer.curr_tok.type == "REGISTER",
            SyntaxError,
            "Expected register token following opcode",
        )
        statement["trf"] = lexer.curr_tok.val
        lexer.advance()
        expect(
            lexer.curr_tok.type == "COMMA",
            SyntaxError,
            "Expected comma following register token in instr %s" % statement,
        )
        lexer.advance()
        statement["mem_operand"] = parse_mem_operand(lexer)
        # TODO: check base reg against load/store type

    # parse RR and RI instrs
    elif statement["opcode"] in parse_lookups.RR_RI_FORMAT_INSTRS_LOOKUP:
        # RR format instr
        expect(
            lexer.curr_tok.type == "REGISTER",
            SyntaxError,
            "Expected register token following opcode",
        )
        statement["dst"] = lexer.curr_tok.val
        lexer.advance()
        expect(
            lexer.curr_tok.type == "COMMA",
            SyntaxError,
            "Expected comma following register token",
        )
        lexer.advance()
        if lexer.curr_tok.type == "NUMBER":
            statement["instr_type"] = "ri_format"
            # RI-format
            expect(
                statement["opcode"] in parse_lookups.RI_FORMAT_INSTRS_LOOKUP,
                SyntaxError,
                "Numeric literal source not allowed for this instruction!",
            )
            statement["immediate"] = lexer.curr_tok.val
            lexer.advance()
        else:
            statement["instr_type"] = "rr_format"
            expect(
                lexer.curr_tok.type == "REGISTER",
                SyntaxError,
                "Expected register token following comma",
            )
            statement["src"] = lexer.curr_tok.val
            lexer.advance()

    # we should be looking at an EOL token right now
    if lexer.curr_tok.type != "EOL":
        raise SyntaxError(
            "Unexpected token '%s' for instruction '%s'"
            % (lexer.curr_tok.val, statement["opcode"])
        )
    return statement


def parse_directive_statement(lexer: lex.lexer):
    statement = {}
    statement["type"] = "directive"
    lexer.advance()
    # TODO: this will have to change when we properly implement directives.
    # For now, the only directive is label definitions, so we can do this.
    statement["subtype"] = "label_def"
    statement["label"] = lexer.curr_tok.val
    lexer.advance()
    expect(
        lexer.curr_tok.type == "COLON",
        SyntaxError,
        "Label definitions must have a colon following them!",
    )
    return statement


def parse_line(line: str):
    # handle empty lines
    if line == "":
        return None
    lexer = lex.lexer(line)
    assert lexer.curr_tok.type == "BEGIN"
    lexer.advance()  # consume beginning of line token
    if lexer.curr_tok.type == "SEMICOLON":
        return None
    elif lexer.curr_tok.type == "STRING":
        # Likely an identifier
        return parse_instr_statement(lexer)
    elif lexer.curr_tok.type == "PERIOD":
        return parse_directive_statement(lexer)
    else:
        raise SyntaxError("Expected line to start with an instruction or directive!")
