
from tests.util.asserts import assert_that, equals, fail
from tests.util.test import test
from tests.util.system_test import system_test
from tests.util.all_examples import all_examples

from cell.lexer import lex
from cell.parser import (
    parse, Assignment, Call, Function, Operation, Number, String, Symbol)

# --- Utils ---


def parsed(inp):
    return list(parse(lex(inp)))

# --- Parsing ---


@test
def Empty_file_produces_nothing():
    assert_that(parsed(""), equals([]))


@test
def Number_is_parsed_as_expression():
    assert_that(parsed("56;"), equals([Number("56")]))


@test
def Sum_of_numbers_is_parsed_as_expression():
    assert_that(
        parsed("32 + 44;"),
        equals(
            [
                Operation("+", Number("32"), Number("44"))
            ]
        )
    )


@test
def Difference_of_symbol_and_number_is_parsed_as_expression():
    assert_that(
        parsed("foo - 44;"),
        equals(
            [
                Operation("-", Symbol("foo"), Number("44"))
            ]
        )
    )


@test
def Multiplication_of_symbols_is_parsed_as_expression():
    assert_that(
        parsed("foo * bar;"),
        equals(
            [
                Operation("*", Symbol("foo"), Symbol("bar"))
            ]
        )
    )


@test
def Variable_assignment_gets_parsed():
    assert_that(
        parsed("x = 3;"),
        equals(
            [
                Assignment(Symbol("x"), Number("3"))
            ]
        )
    )


@test
def Function_call_with_no_args_gets_parsed():
    assert_that(
        parsed("print();"),
        equals(
            [
                Call(Symbol("print"), [])
            ]
        )
    )


@test
def Function_call_with_various_args_gets_parsed():
    assert_that(
        parsed("print( 'a', 3, 4 / 12 );"),
        equals(
            [
                Call(
                    Symbol("print"),
                    [
                        String("a"),
                        Number("3"),
                        Operation("/", Number("4"), Number("12"))
                    ]
                )
            ]
        )
    )


@test
def Multiple_function_calls_with_no_args_get_parsed():
    assert_that(
        parsed("print()();"),
        equals(
            [
                Call(Call(Symbol("print"), []), [])
            ]
        )
    )


@test
def Multiple_function_calls_with_various_args_get_parsed():
    assert_that(
        parsed("print( 'a', 3, 4 / 12 )(512)();"),
        equals(
            [
                Call(
                    Call(
                        Call(
                            Symbol("print"),
                            [
                                String("a"),
                                Number("3"),
                                Operation("/", Number("4"), Number("12"))
                            ]
                        ),
                        [
                            Number("512")
                        ]
                    ),
                    []
                )
            ]
        )
    )


@test
def Assigning_to_a_number_is_an_error():
    try:
        print(parsed("3 = x;"))
        fail("Should throw")
    except Exception as e:
        assert_that(
            str(e),
            equals("You can't assign to anything except a symbol.")
        )


@test
def Assigning_to_an_expression_is_an_error():
    try:
        parsed("x(4) = 5;")
        fail("Should throw")
    except Exception as e:
        assert_that(
            str(e),
            equals("You can't assign to anything except a symbol.")
        )


@test
def Empty_function_definition_gets_parsed():
    assert_that(
        parsed("{};"),
        equals(
            [
                Function([], [])
            ]
        )
    )


@test
def Missing_param_definition_with_colon_is_an_error():
    try:
        parsed("{:print(x););")
        fail("Should throw")
    except Exception as e:
        assert_that(
            str(e),
            equals("Colon must be followed by ( in a function definition.")
        )


@test
def Multiple_commands_parse_into_multiple_expressions():
    program = """
    x = 3;
    func = {:(a) print(a);};
    func(x);
    """
    assert_that(
        parsed(program),
        equals(
            [
                Assignment(Symbol('x'), Number('3')),
                Assignment(
                    Symbol('func'),
                    Function(
                        [Symbol('a')],
                        [
                            Call(Symbol('print'), [Symbol('a')])
                        ]
                    )
                ),
                Call(Symbol('func'), [Symbol('x')])
            ]
        )
    )


@test
def Empty_function_definition_with_params_gets_parsed():
    assert_that(
        parsed("{:(aa, bb, cc, dd)};"),
        equals(
            [
                Function(
                    [
                        Symbol("aa"),
                        Symbol("bb"),
                        Symbol("cc"),
                        Symbol("dd")
                    ],
                    []
                )
            ]
        )
    )


@test
def Function_params_that_are_not_symbols_is_an_error():
    try:
        parsed("{:(aa + 3, d)};"),
        fail("Should throw")
    except Exception as e:
        assert_that(
            str(e),
            equals(
                "Only symbols are allowed in function parameter lists. "
                + "I found:('number', '3')."
            )
        )


@test
def Function_definition_containing_commands_gets_parsed():
    assert_that(
        parsed('{print(3-4); a = "x"; print(a);};'),
        equals(
            [
                Function(
                    [],
                    [
                        Call(
                            Symbol('print'),
                            [
                                Operation('-', Number('3'), Number('4'))
                            ]
                        ),
                        Assignment(Symbol('a'), String('x')),
                        Call(Symbol('print'), [Symbol('a')])
                    ]
                )
            ]
        )
    )


@test
def Function_definition_with_params_and_commands_gets_parsed():
    assert_that(
        parsed('{:(x,yy)print(3-4); a = "x"; print(a);};'),
        equals(
            [
                Function(
                    [
                        Symbol("x"),
                        Symbol("yy")
                    ],
                    [
                        Call(
                            Symbol('print'),
                            [
                                Operation('-', Number('3'), Number('4'))
                            ]
                        ),
                        Assignment(Symbol('a'), String('x')),
                        Call(Symbol('print'), [Symbol('a')])
                    ]
                )
            ]
        )
    )


@test
def A_complex_example_program_parses():
    example = """
        double =
            {:(x)
                2 * x;
            };

        num1 = 3;
        num2 = double( num );

        answer =
            if( greater_than( num2, 5 ),
                {"LARGE!"},
                {"small."}
            );

        print( answer );
    """
    parsed(example)


# --- Example programs ---


@system_test
def All_examples_parse():
    from cell.chars_in_file import chars_in_file
    for example in all_examples():
        with open(example, encoding="ascii") as f:
            parsed(chars_in_file(f))
