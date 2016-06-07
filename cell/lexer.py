import re


def _scan(first_char, chars, allowed):
    assert type(chars) is PeekableStream
    ret = first_char
    p = chars.next
    while p is not None and re.match(allowed, p):
        ret += chars.move_next()
        p = chars.next
    return ret


def _scan_string(delim, chars):
    assert type(chars) is PeekableStream
    ret = ""
    while chars.next != delim:
        c = chars.move_next()
        if c is None:
            raise Exception("A string ran off the end of the program!")
        ret += c
    chars.move_next()
    return ret


class PeekableStream:

    def __init__(self, iterator):
        self.iterator = iter(iterator)
        self._fill()

    def _fill(self):
        try:
            self.next = next(self.iterator)
        except StopIteration:
            self.next = None

    def move_next(self):
        ret = self.next
        self._fill()
        return ret


def lex(chars_iter):
    chars = PeekableStream(chars_iter)
    while chars.next is not None:
        c = chars.move_next()
        if c in "(){},;=:":
            yield (c, "")
        elif c in " \n":
            pass
        elif c in ("'", '"'):
            yield ("string", _scan_string(c, chars))
        elif c in "+-*/":
            yield ("arithmetic", c)
        elif re.match("[.0-9]", c):
            yield ("number", _scan(c, chars, "[.0-9]"))
        elif re.match("[_a-zA-Z]", c):
            yield ("symbol", _scan(c, chars, "[_a-zA-Z0-9]"))
        elif c == "\t":
            raise Exception("Tab characters are not allowed in Cell")
        else:
            raise Exception("Unrecognised character: '" + c + "'.")
