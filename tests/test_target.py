"""Functional tests for target.py (all 16 functions).

Each section covers: valid inputs, boundary values, invalid values and wrong types.
Run with:  pytest --cov=target --cov-branch
"""

import math

import pytest

import target


def assert_same(result, expected):
    """Check both the value and the exact type of a result."""
    assert type(result) is type(expected), f"{type(result)} != {type(expected)}"
    assert result == expected


# ---------------------------------------------------------------------------
# 1. is_adult (integer)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "age, expected",
    [
        (0, False),
        (1, False),
        (17, False),
        (18, True),
        (19, True),
        (65, True),
        (150, True),
        (17.99, False),
        (18.0, True),
    ],
    ids=["zero", "one", "just-below-18", "exactly-18", "just-above-18",
         "senior", "very-old", "float-below", "float-boundary"],
)
def test_is_adult_valid(age, expected):
    assert target.is_adult(age) is expected


@pytest.mark.parametrize("age", [-1, -18, -0.5, -1000])
def test_is_adult_negative_raises(age):
    with pytest.raises(ValueError, match="age cannot be negative"):
        target.is_adult(age)


@pytest.mark.parametrize("bad", ["18", None, [18], (18,), {"age": 18}])
def test_is_adult_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.is_adult(bad)


# ---------------------------------------------------------------------------
# 2. celsius_to_fahrenheit (float)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "celsius, expected",
    [
        (0, 32.0),
        (100, 212.0),
        (-40, -40.0),
        (37, 98.6),
        (36.6, 97.88),
        (0.01, 32.02),
        (-273.15, -459.67),
        (-17.78, 0.0),
        (1000, 1832.0),
    ],
    ids=["freezing", "boiling", "equal-point", "body-int", "body-float",
         "rounds-to-2dp", "absolute-zero", "near-zero-f", "very-hot"],
)
def test_celsius_to_fahrenheit_valid(celsius, expected):
    assert_same(target.celsius_to_fahrenheit(celsius), expected)


def test_celsius_to_fahrenheit_rounds_to_two_decimals():
    # 36.666 C = 97.9988 F, which must round to 98.0
    assert_same(target.celsius_to_fahrenheit(36.666), 98.0)
    # 21.111 C = 70.0 F after rounding
    assert_same(target.celsius_to_fahrenheit(21.111), 70.0)


@pytest.mark.parametrize("bad", ["20", "", None, [20], {"c": 20}])
def test_celsius_to_fahrenheit_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.celsius_to_fahrenheit(bad)


# ---------------------------------------------------------------------------
# 3. count_vowels (string)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text, expected",
    [
        ("", 0),
        ("bcdfg", 0),
        ("aeiou", 5),
        ("AEIOU", 5),
        ("Hello World", 3),
        ("rhythm", 0),
        ("yY", 0),
        ("aaaa", 4),
        ("a1e2i3o4u5", 5),
        ("  a  ", 1),
        ("PYTHON", 1),
        ("\u00e9\u00e8", 0),
    ],
    ids=["empty", "no-vowels", "all-lower", "all-upper", "mixed-case",
         "y-not-vowel-word", "y-only", "repeated", "digits-between",
         "spaces", "uppercase-word", "accented-not-counted"],
)
def test_count_vowels_valid(text, expected):
    assert_same(target.count_vowels(text), expected)


@pytest.mark.parametrize("bad", [None, 123, 1.5, True, ["a"], ("a",), b"abc", {"a"}])
def test_count_vowels_wrong_type_raises(bad):
    with pytest.raises(TypeError, match="text must be a string"):
        target.count_vowels(bad)


# ---------------------------------------------------------------------------
# 4. invert (boolean)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("flag, expected", [(True, False), (False, True)])
def test_invert_valid(flag, expected):
    assert target.invert(flag) is expected


def test_invert_twice_returns_original():
    assert target.invert(target.invert(True)) is True
    assert target.invert(target.invert(False)) is False


@pytest.mark.parametrize("bad", [0, 1, -1, 1.0, "True", "", None, [], [True]])
def test_invert_wrong_type_raises(bad):
    with pytest.raises(TypeError, match="flag must be True or False"):
        target.invert(bad)


# ---------------------------------------------------------------------------
# 5. greet (None / default argument)
# ---------------------------------------------------------------------------
def test_greet_default_argument_is_guest():
    assert target.greet() == "Hello, Guest!"


@pytest.mark.parametrize(
    "name, expected",
    [
        (None, "Hello, Guest!"),
        ("", "Hello, Guest!"),
        (" ", "Hello, Guest!"),
        ("     ", "Hello, Guest!"),
        ("\t\n", "Hello, Guest!"),
        ("Sakib", "Hello, Sakib!"),
        ("  Sakib  ", "Hello, Sakib!"),
        ("\tSakib\n", "Hello, Sakib!"),
        ("Mary Ann", "Hello, Mary Ann!"),
        ("  Mary  Ann ", "Hello, Mary  Ann!"),
        ("A", "Hello, A!"),
        ("0", "Hello, 0!"),
        ("guest", "Hello, guest!"),
    ],
    ids=["none", "empty", "one-space", "many-spaces", "tab-newline",
         "plain", "padded", "tab-padded", "inner-space", "inner-double-space",
         "single-char", "zero-string", "lowercase-guest"],
)
def test_greet_values(name, expected):
    assert target.greet(name) == expected


def test_greet_keyword_argument():
    assert target.greet(name="Rahim") == "Hello, Rahim!"


@pytest.mark.parametrize("bad", [123, 1.5, True, ["Sakib"], {"name": "x"}])
def test_greet_non_string_raises_attribute_error(bad):
    # Documented behaviour: no explicit type check, so .strip() fails.
    with pytest.raises(AttributeError, match="strip"):
        target.greet(bad)


# ---------------------------------------------------------------------------
# 6. find_max (list)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "numbers, expected",
    [
        ([1, 2, 3], 3),
        ([3, 2, 1], 3),
        ([2, 9, 4], 9),
        ([5], 5),
        ([0], 0),
        ([-5, -1, -3], -1),
        ([7, 7, 7], 7),
        ([1.5, 2.5, 2.4], 2.5),
        ([1, 2.5], 2.5),
        ([3, 2.5], 3),
        ([-1, 0, 1], 1),
        ((4, 8, 6), 8),
        ([10**20, 1], 10**20),
        ([float("-inf"), -1], -1),
        ([1, float("inf")], float("inf")),
    ],
    ids=["ascending", "descending", "max-in-middle", "single", "single-zero",
         "all-negative", "all-equal", "floats", "int-and-float",
         "int-wins-over-float", "around-zero", "tuple-input", "big-int",
         "neg-infinity", "pos-infinity"],
)
def test_find_max_valid(numbers, expected):
    assert target.find_max(numbers) == expected


def test_find_max_keeps_type_of_winner():
    assert_same(target.find_max([1, 2.5]), 2.5)
    assert_same(target.find_max([3, 2.5]), 3)


def test_find_max_does_not_modify_input():
    data = [3, 1, 2]
    target.find_max(data)
    assert data == [3, 1, 2]


@pytest.mark.parametrize("empty", [[], (), ""])
def test_find_max_empty_raises(empty):
    with pytest.raises(ValueError, match="list is empty"):
        target.find_max(empty)


@pytest.mark.parametrize("bad", [None, 5, 1.5, [1, "a"], [None, 1]])
def test_find_max_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.find_max(bad)


# ---------------------------------------------------------------------------
# 7. get_price (dictionary)
# ---------------------------------------------------------------------------
PRICES = {"apple": 1.5, "bread": 2, "free": 0, "none": None, 10: 99}


@pytest.mark.parametrize(
    "item, expected",
    [("apple", 1.5), ("bread", 2), ("free", 0), ("none", None), (10, 99)],
    ids=["float-price", "int-price", "zero-price", "none-price", "int-key"],
)
def test_get_price_found(item, expected):
    result = target.get_price(PRICES, item)
    assert result == expected
    assert type(result) is type(expected)


@pytest.mark.parametrize("item", ["milk", "Apple", " apple", "", None, "10", 11])
def test_get_price_missing_raises_key_error(item):
    with pytest.raises(KeyError):
        target.get_price(PRICES, item)


def test_get_price_missing_message():
    with pytest.raises(KeyError, match="milk not found"):
        target.get_price(PRICES, "milk")


def test_get_price_empty_dictionary_raises():
    with pytest.raises(KeyError, match="apple not found"):
        target.get_price({}, "apple")


@pytest.mark.parametrize(
    "prices, item",
    [(None, "apple"), (5, "apple"), ({}, ["apple"]), ({"a": 1}, {"a": 1})],
    ids=["none-dict", "int-dict", "unhashable-list-item", "unhashable-dict-item"],
)
def test_get_price_wrong_type_raises(prices, item):
    with pytest.raises(TypeError):
        target.get_price(prices, item)


def test_get_price_list_instead_of_dict_raises():
    with pytest.raises(TypeError):
        target.get_price(["apple"], "apple")


# ---------------------------------------------------------------------------
# 8. swap (tuple)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "pair, expected",
    [
        ((1, 2), (2, 1)),
        ((2, 1), (1, 2)),
        (("a", "b"), ("b", "a")),
        ((1, "a"), ("a", 1)),
        ((None, 0), (0, None)),
        ((5, 5), (5, 5)),
        (((1, 2), 3), (3, (1, 2))),
        ([1, 2], (2, 1)),
        ("ab", ("b", "a")),
    ],
    ids=["ints", "reversed-ints", "strings", "mixed-types", "none-and-zero",
         "equal-values", "nested", "list-input", "string-input"],
)
def test_swap_valid(pair, expected):
    assert_same(target.swap(pair), expected)


def test_swap_twice_returns_original():
    assert target.swap(target.swap((1, 2))) == (1, 2)


@pytest.mark.parametrize(
    "pair",
    [(), (1,), (1, 2, 3), [], [1], [1, 2, 3], "", "abc"],
    ids=["empty-tuple", "one-tuple", "three-tuple", "empty-list",
         "one-list", "three-list", "empty-string", "three-chars"],
)
def test_swap_wrong_length_raises(pair):
    with pytest.raises(ValueError, match="pair must have exactly 2 values"):
        target.swap(pair)


@pytest.mark.parametrize("bad", [None, 5, 1.5, True])
def test_swap_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.swap(bad)


# ---------------------------------------------------------------------------
# 9. common_items (set)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "set_a, set_b, expected",
    [
        ({1, 2, 3}, {2, 3, 4}, {2, 3}),
        ({1, 2}, {3, 4}, set()),
        (set(), {1, 2}, set()),
        ({1, 2}, set(), set()),
        (set(), set(), set()),
        ({1, 2, 3}, {1, 2, 3}, {1, 2, 3}),
        ({1, 2, 3}, {2}, {2}),
        ({"a", "b"}, {"b", "c"}, {"b"}),
        ({1, "1"}, {"1", 2}, {"1"}),
        ({(1, 2)}, {(1, 2), (3, 4)}, {(1, 2)}),
    ],
    ids=["overlap", "disjoint", "first-empty", "second-empty", "both-empty",
         "identical", "subset", "strings", "int-vs-string", "tuples"],
)
def test_common_items_valid(set_a, set_b, expected):
    result = target.common_items(set_a, set_b)
    assert isinstance(result, set)
    assert result == expected


def test_common_items_is_symmetric():
    a, b = {1, 2, 3}, {3, 4}
    assert target.common_items(a, b) == target.common_items(b, a)


def test_common_items_does_not_modify_inputs():
    a, b = {1, 2, 3}, {2, 3, 4}
    target.common_items(a, b)
    assert a == {1, 2, 3}
    assert b == {2, 3, 4}


def test_common_items_frozenset_input_gives_frozenset():
    result = target.common_items(frozenset({1, 2}), {2, 3})
    assert result == {2}
    assert isinstance(result, frozenset)


@pytest.mark.parametrize(
    "set_a, set_b",
    [
        ([1, 2], [2, 3]),
        ({1, 2}, [2, 3]),
        ("abc", "bcd"),
        (None, {1}),
        ({1}, None),
        ({"a": 1}, {"a": 1}),
    ],
    ids=["two-lists", "set-and-list", "two-strings", "none-first", "none-second",
         "two-dicts"],
)
def test_common_items_wrong_type_raises(set_a, set_b):
    with pytest.raises(TypeError):
        target.common_items(set_a, set_b)


# ---------------------------------------------------------------------------
# 10. is_leap_year (date)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "year, expected",
    [
        (1, False),
        (2, False),
        (3, False),
        (4, True),
        (100, False),
        (200, False),
        (400, True),
        (600, False),
        (800, True),
        (1896, True),
        (1900, False),
        (2000, True),
        (2001, False),
        (2004, True),
        (2023, False),
        (2024, True),
        (2100, False),
        (2400, True),
        (9999, False),
    ],
    ids=["year-1", "year-2", "year-3", "year-4", "century-100", "century-200",
         "century-400", "century-600", "century-800",
         "1896", "1900-century", "2000-century", "2001", "2004", "2023", "2024",
         "2100-century", "2400-century", "9999"],
)
def test_is_leap_year_valid(year, expected):
    assert target.is_leap_year(year) is expected


@pytest.mark.parametrize("year", [0, -1, -4, -400, -2000, 0.5])
def test_is_leap_year_below_one_raises(year):
    with pytest.raises(ValueError, match="year must be 1 or more"):
        target.is_leap_year(year)


@pytest.mark.parametrize("bad", ["2000", None, [2000], (2000,), {2000}])
def test_is_leap_year_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.is_leap_year(bad)


# ---------------------------------------------------------------------------
# 11. to_int (type conversion)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected",
    [
        (42, 42),
        (0, 0),
        (-7, -7),
        ("42", 42),
        ("-7", -7),
        ("0", 0),
        ("  42  ", 42),
        ("+5", 5),
        ("007", 7),
        ("1_000", 1000),
        (3.9, 3),
        (-3.9, -3),
        (0.99, 0),
        (-0.5, 0),
        (1e3, 1000),
        (b"12", 12),
        (10**30, 10**30),
    ],
    ids=["int", "zero", "negative", "str", "negative-str", "zero-str", "padded-str",
         "plus-sign", "leading-zeros", "underscore", "truncates-up", "truncates-negative",
         "below-one", "negative-half", "exponent-float", "bytes", "huge-int"],
)
def test_to_int_valid(value, expected):
    assert_same(target.to_int(value), expected)


@pytest.mark.parametrize("flag", [True, False])
def test_to_int_bool_raises(flag):
    with pytest.raises(TypeError, match="bool is not allowed"):
        target.to_int(flag)


@pytest.mark.parametrize("bad", ["abc", "", " ", "3.5", "1e3", "4 2", "0x10", "--1",
                                 "nan", float("nan")])
def test_to_int_bad_value_raises_value_error(bad):
    with pytest.raises(ValueError):
        target.to_int(bad)


@pytest.mark.parametrize("bad", [None, [1], (1,), {1}, {"a": 1}, 1 + 2j])
def test_to_int_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.to_int(bad)


@pytest.mark.parametrize("bad", [float("inf"), float("-inf")])
def test_to_int_infinity_raises_overflow(bad):
    with pytest.raises(OverflowError):
        target.to_int(bad)


# ---------------------------------------------------------------------------
# 12. divide (math)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 2, 5.0),
        (4, 2, 2.0),
        (7, 2, 3.5),
        (-6, 3, -2.0),
        (6, -3, -2.0),
        (-6, -3, 2.0),
        (0, 5, 0.0),
        (5, 1, 5.0),
        (5, 5, 1.0),
        (1, 4, 0.25),
        (1.5, 0.5, 3.0),
        (10**20, 10**10, 1e10),
    ],
    ids=["ints", "exact-int-result", "fraction", "negative-numerator",
         "negative-denominator", "both-negative", "zero-numerator", "divide-by-one",
         "divide-by-self", "quarter", "floats", "huge"],
)
def test_divide_exact(a, b, expected):
    assert_same(target.divide(a, b), expected)


def test_divide_inexact_result():
    assert target.divide(1, 3) == pytest.approx(0.3333333333333333)
    assert target.divide(2, 3) == pytest.approx(0.6666666666666666)


def test_divide_tiny_divisor_is_allowed():
    assert target.divide(1, 1e-10) == pytest.approx(1e10)


@pytest.mark.parametrize("a, b", [(5, 0), (0, 0), (-5, 0), (5, 0.0), (5, -0.0), (1.5, 0)])
def test_divide_by_zero_raises(a, b):
    with pytest.raises(ZeroDivisionError, match="cannot divide by zero"):
        target.divide(a, b)


@pytest.mark.parametrize(
    "a, b",
    [("a", 2), (2, "a"), (None, 2), (2, None), ([1], 2), (4, "2")],
)
def test_divide_wrong_type_raises(a, b):
    with pytest.raises(TypeError):
        target.divide(a, b)


# ---------------------------------------------------------------------------
# 13. power (math)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "base, exponent, expected",
    [
        (2, 3, 8),
        (2, 0, 1),
        (0, 0, 1),
        (0, 5, 0),
        (5, 1, 5),
        (1, 1000, 1),
        (-2, 3, -8),
        (-2, 2, 4),
        (-1, 101, -1),
        (10, 2, 100),
        (10**10, 2, 10**20),
        (2, 100, 2**100),
        (2, -1, 0.5),
        (10, -2, 0.01),
        (2.5, 2, 6.25),
        (0.0, 3, 0.0),
    ],
    ids=["basic", "exp-zero", "zero-zero", "zero-base", "exp-one", "one-base",
         "negative-odd", "negative-even", "minus-one-odd", "hundred",
         "big-base", "big-result-exact", "negative-exp", "negative-exp-fraction",
         "float-base", "float-zero-base"],
)
def test_power_exact(base, exponent, expected):
    assert_same(target.power(base, exponent), expected)


def test_power_fractional_exponent_is_inexact():
    assert target.power(4, 0.5) == pytest.approx(2.0)
    assert target.power(2, 0.5) == pytest.approx(1.4142135623730951)
    assert target.power(8, 1 / 3) == pytest.approx(2.0)


def test_power_negative_base_fractional_exponent_gives_complex():
    result = target.power(-8, 0.5)
    assert isinstance(result, complex)
    assert result.imag == pytest.approx(math.sqrt(8))


def test_power_zero_to_negative_raises():
    with pytest.raises(ZeroDivisionError):
        target.power(0, -1)


def test_power_float_overflow_raises():
    with pytest.raises(OverflowError):
        target.power(10.0, 400)


@pytest.mark.parametrize(
    "base, exponent",
    [("a", 2), (2, "a"), (None, 2), (2, None), ([2], 2), ("2", "2")],
)
def test_power_wrong_type_raises(base, exponent):
    with pytest.raises(TypeError):
        target.power(base, exponent)


# ---------------------------------------------------------------------------
# 14. square_root (math)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "x, expected",
    [
        (0, 0.0),
        (1, 1.0),
        (4, 2.0),
        (9, 3.0),
        (0.25, 0.5),
        (100, 10.0),
        (1e300, 1e150),
        (10**20, 1e10),
        (float("inf"), float("inf")),
    ],
    ids=["zero", "one", "four", "nine", "fraction", "hundred", "huge-float",
         "huge-int", "infinity"],
)
def test_square_root_exact(x, expected):
    assert_same(target.square_root(x), expected)


def test_square_root_inexact_result():
    assert target.square_root(2) == pytest.approx(1.4142135623730951)
    assert target.square_root(0.5) == pytest.approx(0.7071067811865476)


def test_square_root_nan_returns_nan():
    assert math.isnan(target.square_root(float("nan")))


@pytest.mark.parametrize("x", [-1, -0.0001, -100, -1e300, float("-inf")])
def test_square_root_negative_raises(x):
    with pytest.raises(ValueError, match="cannot take the square root of a negative number"):
        target.square_root(x)


def test_square_root_int_too_large_raises_overflow():
    with pytest.raises(OverflowError):
        target.square_root(10**400)


@pytest.mark.parametrize("bad", ["4", None, [4], (4,), {4}])
def test_square_root_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.square_root(bad)


# ---------------------------------------------------------------------------
# 15. factorial (math)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 6),
        (4, 24),
        (5, 120),
        (6, 720),
        (10, 3628800),
        (20, 2432902008176640000),
        (25, 15511210043330985984000000),
    ],
)
def test_factorial_valid(n, expected):
    assert_same(target.factorial(n), expected)


def test_factorial_matches_standard_library():
    for n in range(0, 30):
        assert target.factorial(n) == math.factorial(n)


@pytest.mark.parametrize("n", [-1, -2, -100, -0.5])
def test_factorial_negative_raises(n):
    with pytest.raises(ValueError, match="factorial is not defined for negative numbers"):
        target.factorial(n)


@pytest.mark.parametrize("bad", [2.5, 3.0, "5", None, [3], (3,)])
def test_factorial_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.factorial(bad)


# ---------------------------------------------------------------------------
# 16. average (math)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "numbers, expected",
    [
        ([1, 2, 3], 2.0),
        ([5], 5.0),
        ([0], 0.0),
        ([1, 2], 1.5),
        ([0, 0, 0], 0.0),
        ([-1, -2, -3], -2.0),
        ([-5, 5], 0.0),
        ([2, 4, 6, 8], 5.0),
        ([1.5, 2.5], 2.0),
        ([1, 2.5], 1.75),
        ((1, 2, 3), 2.0),
        ([10**20, 10**20], 1e20),
        ([100, 0], 50.0),
    ],
    ids=["basic", "single", "single-zero", "fraction", "zeros", "negatives",
         "cancel-out", "even-count", "floats", "mixed", "tuple-input", "huge", "with-zero"],
)
def test_average_exact(numbers, expected):
    assert_same(target.average(numbers), expected)


def test_average_inexact_result():
    assert target.average([0.1, 0.2, 0.3]) == pytest.approx(0.2)
    assert target.average([1, 1, 2]) == pytest.approx(1.3333333333333333)


def test_average_overflow_gives_infinity():
    assert math.isinf(target.average([1e308, 1e308]))


def test_average_does_not_modify_input():
    data = [1, 2, 3]
    target.average(data)
    assert data == [1, 2, 3]


@pytest.mark.parametrize("empty", [[], (), ""])
def test_average_empty_raises(empty):
    with pytest.raises(ValueError, match="list is empty"):
        target.average(empty)


@pytest.mark.parametrize("bad", [None, 5, 1.5, ["a", "b"], [1, "a"], [None], "abc"])
def test_average_wrong_type_raises(bad):
    with pytest.raises(TypeError):
        target.average(bad)
