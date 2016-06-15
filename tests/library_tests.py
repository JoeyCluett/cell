
from io import StringIO

from tests.util.asserts import assert_that, assert_fails, equals
from tests.util.test import test

from pycell.env import Env
from pycell.eval_ import eval_list
from pycell.lexer import lex
from pycell.parser import parse

import pycell.library

# --- Utils


def evald(inp, stdout=None):
    env = Env(stdout=stdout)
    pycell.library.import_(env)
    return eval_list(parse(lex(inp)), env)


# --- Tests


@test
def if_calls_then_if_first_argument_is_nonzero():
    assert_that(
        evald('if( 1, {"t";}, {"f";} );'),
        equals(evald('"t";'))
    )


@test
def if_calls_else_if_first_argument_is_zero():
    assert_that(
        evald('if( 0, {"t";}, {"f";} );'),
        equals(evald('"f";'))
    )


@test
def Call_if_with_a_nonnumber_is_an_error():
    assert_fails(
        "Only numbers may be passed to an if, but I was passed "
        + "'('string', 'x')'",
        evald,
        'if("x", {}, {});'
    )


@test
def Equals_returns_true_for_identical_numbers():
    assert_that(
        evald('if(equals(1, 1), {4;}, {5;});'),
        equals(evald("4;"))
    )


@test
def Equals_returns_false_for_different_numbers():
    assert_that(
        evald('if(equals(1, 2), {4;}, {5;});'),
        equals(evald("5;"))
    )


@test
def Equals_returns_false_for_different_types():
    assert_that(
        evald('if(equals(1, "1"), {4;}, {5;});'),
        equals(evald("5;"))
    )


@test
def Functions_are_not_equal_even_if_the_same():
    assert_that(
        evald('if(equals({3;}, {3;}), {4;}, {5;});'),
        equals(evald("5;"))
    )


@test
def Print_prints_to_stdout():
    stdout = StringIO()
    evald('print("foo");', stdout=stdout)
    assert_that(stdout.getvalue(), equals("foo\n"))


@test
def Print_returns_None():
    stdout = StringIO()
    assert_that(evald('print("foo");', stdout=stdout), equals(("none",)))
