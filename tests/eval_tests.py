
from tests.util.asserts import assert_that, assert_fails, equals
from tests.util.test import test

from pycell.lexer import lex
from pycell.parser import parse
from pycell.eval_ import eval_expr, eval_list
from pycell.env import Env

# --- Utils ---

def evald(inp, env=None):
    if env is None:
        env = Env()
    return eval_list(parse(lex(inp)), env)


def assert_prog_fails(program, error, env=None):
    assert_fails(error, evald, program, env)


# --- Evaluating ---


@test
def Evaluating_an_empty_program_gives_none():
    assert_that(evald(""), equals(("none",)))


@test
def Evaluating_a_primitive_returns_itself():
    assert_that(evald("3;"), equals(("number", 3)))
    assert_that(evald("3.1;"), equals(("number", 3.1)))
    assert_that(evald("'foo';"), equals(("string", "foo")))


@test
def Arithmetic_expressions_come_out_correct():
    assert_that(evald("3 + 4;"), equals(("number", 7)))
    assert_that(evald("3 - 4;"), equals(("number", -1)))
    assert_that(evald("3 * 4;"), equals(("number", 12)))
    assert_that(evald("3 / 4;"), equals(("number", 0.75)))


@test
def Referring_to_an_unknown_symbol_is_an_error():
    assert_prog_fails("x;", "Unknown symbol 'x'.")


@test
def Can_define_a_value_and_retrieve_it():
    assert_that(evald("x = 30;x;"), equals(("number", 30)))
    assert_that(evald("y = 'foo';y;"), equals(("string", "foo")))


@test
def Value_of_an_assignment_is_the_value_assigned():
    assert_that(evald("x = 31;"), equals(("number", 31)))


@test
def None_evaluates_to_None():
    assert_that(eval_expr(("none",), Env()), equals(("none", )))


@test
def Calling_a_function_returns_its_last_value():
    assert_that(
        evald("{10;11;}();"),
        equals(("number", 11))
    )


@test
def Body_of_a_function_can_use_arg_values():
    assert_that(
        evald("{:(x, y) x + y;}(100, 1);"),
        equals(("number", 101))
    )


@test
def Can_hold_a_reference_to_a_function_and_call_it():
    assert_that(
        evald("""
        add = {:(x, y) x + y;};
        add(20, 2.2);
        """),
        equals(("number", 22.2))
    )


@test
def A_symbol_has_different_life_inside_and_outside_a_function():
    """Define a symbol outside a function, redefine inside,
       then evaluate outside.  What happened inside the
       function should not affect the value outside."""

    assert_that(
        evald("""
            foo = "bar";
            {foo = 3;}();
            foo;
        """),
        equals(("string", "bar"))
    )


@test
def A_symbol_within_a_function_has_the_local_value():
    assert_that(
        evald("""
            foo = 3;
            bar = {foo = 77;foo;}();
            bar;
        """),
        equals(("number", 77))
    )


@test
def Native_function_gets_called():
    def native_fn(env, x, y):
        return ("number", x[1] + y[1])
    env = Env()
    env.set("native_fn", ("native", native_fn))
    assert_that(evald("native_fn( 2, 8 );", env), equals(("number", 10)))


@test
def Wrong_number_of_arguments_to_a_function_is_an_error():
    assert_prog_fails(
        "{}(3);",
        "1 arguments passed to function, but it requires 0 arguments."
    )
    assert_prog_fails(
        "x={:(a, b, c)}; x(3, 2);",
        "2 arguments passed to function, but it requires 3 arguments."
    )


@test
def Wrong_number_of_arguments_to_a_native_function_is_an_error():
    def native_fn0(env):
        return ("number", 12)

    def native_fn3(env, x, y, z):
        return ("number", 12)
    env = Env()
    env.set("native_fn0", ("native", native_fn0))
    env.set("native_fn3", ("native", native_fn3))
    assert_prog_fails(
        "native_fn0(3);",
        "1 arguments passed to function, but it requires 0 arguments.",
        env
    )
    assert_prog_fails(
        "native_fn3(3, 2);",
        "2 arguments passed to function, but it requires 3 arguments.",
        env
    )


@test
def Function_arguments_are_independent():
    assert_that(evald(
        """
        fn = {:(x) {x;};};
        a = fn("a");
        b = fn("b");
        a();
        """
        ),
        equals(evald("'a';"))
    )
    assert_that(evald(
        """
        fn = {:(x) {x;};};
        a = fn("a");
        b = fn("b");
        b();
        """
        ),
        equals(evald("'b';"))
    )


@test
def A_native_function_can_edit_the_environment():
    def mx3(env):
        env.set("x", ("number", 3))
    env = Env()
    env.set("make_x_three", ("native", mx3))
    assert_that(
        evald("x=1;make_x_three();x;", env),
        equals(("number", 3))
    )


@test
def A_closure_holds_updateable_values():
    def dumb_set(env, sym, val):
        env.parent.parent.parent.set(sym[1], val)

    def dumb_if_equal(env, val1, val2, then_fn, else_fn):
        if val1 == val2:
            ret = then_fn
        else:
            ret = else_fn
        return eval_expr(("call", ret, []), env)
    env = Env()
    env.set("dumb_set", ("native", dumb_set))
    env.set("dumb_if_equal", ("native", dumb_if_equal))
    assert_that(
        evald(
            """
            counter = {
                x = 0;
                {:(meth)
                    dumb_if_equal(meth, "get",
                        {x;},
                        {dumb_set("x", x + 1);}
                    );
                }
            }();
            counter("inc");
            counter("inc");
            counter("get");
            """,
            env
        ),
        equals(("number", 2))
    )
