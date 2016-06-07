
from cell.peekablestream import PeekableStream
from cell.valueclass import valueclass


def _parse_symbol(tokens):
    token = tokens.next
    if token is None:
        raise Exception("Expecting the name of symbol.")
    typ, val = token

    tokens.move_next()
    if typ == "symbol":
        return Symbol(val)
    else:
        raise Exception(
            "Only symbols are allowed in function parameter lists."
            + " I found:" + str(token) + "."
        )


def _parse_params(tokens):
    ret = []
    if tokens.next[0] != ":":
        return ret
    tokens.move_next()
    typ = tokens.next[0]
    if typ != "(":
        raise Exception("Colon must be followed by ( in a function definition.")
    tokens.move_next()
    typ = tokens.next[0]
    if typ != ")":
        while typ != ")":
            ret.append(_parse_symbol(tokens))
            typ = tokens.next[0]
            tokens.move_next()
            if tokens.next is None:
                raise Exception(
                    "A function parameter list ran off the end of the program.")
    else:
        tokens.move_next()
    return ret


def _parse_commands(tokens):
    ret = []
    if tokens.next is None:
        raise Exception("A function definition ran off the end of the program.")
    typ = tokens.next[0]
    if typ != "}":
        while typ != "}":
            p = _parse(None, tokens, ";}")
            if p is not None:
                ret.append(p)
            typ = tokens.next[0]
            tokens.move_next()
            if tokens.next is None:
                raise Exception(
                    "A function definition ran off the end of the program.")
    else:
        tokens.move_next()
    return ret


def _parse_args(tokens):
    ret = []
    if tokens.next is None:
        raise Exception("An argument list ran off the end of the program.")
    typ = tokens.next[0]
    if typ != ")":
        while typ != ")":
            ret.append(_parse(None, tokens, ",)"))
            typ = tokens.next[0]
            tokens.move_next()
            if tokens.next is None:
                raise Exception(
                    "An argument list ran off the end of the program.")
    else:
        tokens.move_next()
    return ret


def _parse(expr, tokens, stop_at):
    token = tokens.next
    if token is None:
        return expr
    typ, val = token
    if typ in stop_at:
        return expr

    tokens.move_next()
    if typ == "number":
        if expr is not None:
            raise Exception("You can't have a number after: " + str(expr))
        else:
            return _parse(Number(val), tokens, stop_at)
    elif typ == "string":
        if expr is not None:
            raise Exception("You can't have a string after: " + str(expr))
        else:
            return _parse(String(val), tokens, stop_at)
    elif typ == "symbol":
        if expr is not None:
            raise Exception("You can't have a symbol after: " + str(expr))
        else:
            return _parse(Symbol(val), tokens, stop_at)
    elif typ == "operation":
        return _parse(
            Operation(val, expr, _parse(None, tokens, stop_at)),
            tokens,
            stop_at
        )
    elif typ == "(":
        return _parse(Call(expr, _parse_args(tokens)), tokens, stop_at)
    elif typ == "{":
        params = _parse_params(tokens)
        commands = _parse_commands(tokens)
        return _parse(Function(params, commands), tokens, stop_at)
    elif typ == "=":
        if type(expr) != Symbol:
            raise Exception("You can't assign to anything except a symbol.")
        return _parse(
            Assignment(expr, _parse(None, tokens, stop_at)), tokens, stop_at)
    else:
        raise Exception("Unexpected token: " + str(token))


def parse(tokens_iterator):
    tokens = PeekableStream(tokens_iterator)
    while tokens.next is not None:
        p = _parse(None, tokens, ";")
        if p is not None:
            yield p
        tokens.move_next()


@valueclass("name", "value")
class Assignment:
    pass


@valueclass("function", "arguments")
class Call:
    pass


@valueclass("parameters", "commands")
class Function:
    pass


@valueclass("value")
class Number:
    pass


@valueclass("operator", "value1", "value2")
class Operation:
    pass


@valueclass("value")
class String:
    pass


@valueclass("value")
class Symbol:
    pass
