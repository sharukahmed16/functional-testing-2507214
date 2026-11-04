"""Small Flask app that runs the functions in target.py and shows each result or error.

Routes
  GET  /               the web frontend
  GET  /health         {"status": "ok", "sha": "<deployed commit SHA>"}
  GET  /api/functions  description of the 16 functions (used by the frontend)
  POST /api/call       {"function": "is_adult", "inputs": ["18"]}
"""

import json
import math
import os

from flask import Flask, jsonify, request, send_from_directory

import target

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)


def get_commit_sha():
    """Return the commit SHA of the running deployment.

    Render sets RENDER_GIT_COMMIT, Railway sets RAILWAY_GIT_COMMIT_SHA and
    COMMIT_SHA can be used on any other host.
    """
    for name in ("RENDER_GIT_COMMIT", "RAILWAY_GIT_COMMIT_SHA", "COMMIT_SHA"):
        value = os.environ.get(name)
        if value:
            return value
    return "unknown"


def _example(label, *inputs):
    return {"label": label, "inputs": list(inputs)}


# Everything the frontend needs to draw one function: spec text, parameter names
# and ready-made examples (valid values, boundaries and error cases).
FUNCTIONS = [
    {
        "name": "is_adult", "group": "Data types", "type": "Integer",
        "spec": "True if age is 18 or more. A negative age raises ValueError.",
        "params": ["age"],
        "examples": [_example("18 (boundary)", "18"), _example("17", "17"),
                     _example("-1 (error)", "-1"), _example("\"18\" (wrong type)", '"18"')],
    },
    {
        "name": "celsius_to_fahrenheit", "group": "Data types", "type": "Float",
        "spec": "Convert Celsius to Fahrenheit, rounded to 2 decimals.",
        "params": ["celsius"],
        "examples": [_example("37", "37"), _example("36.666 (rounding)", "36.666"),
                     _example("-40", "-40"), _example("\"hot\" (wrong type)", '"hot"')],
    },
    {
        "name": "count_vowels", "group": "Data types", "type": "String",
        "spec": "Count vowels (a, e, i, o, u), ignoring case. A non-string raises TypeError.",
        "params": ["text"],
        "examples": [_example("Hello World", '"Hello World"'), _example("AEIOU", '"AEIOU"'),
                     _example("empty string", '""'), _example("123 (wrong type)", "123")],
    },
    {
        "name": "invert", "group": "Data types", "type": "Boolean",
        "spec": "Return the opposite of flag. A non-bool raises TypeError.",
        "params": ["flag"],
        "examples": [_example("true", "true"), _example("false", "false"),
                     _example("1 (error)", "1")],
    },
    {
        "name": "greet", "group": "Data types", "type": "None",
        "spec": "Greet by name, or greet \"Guest\" if name is None, empty or only spaces.",
        "params": ["name"],
        "examples": [_example("Sakib", '"Sakib"'), _example("None", "null"),
                     _example("only spaces", '"   "'), _example("42 (error)", "42")],
    },
    {
        "name": "find_max", "group": "Data types", "type": "List",
        "spec": "Return the largest number. An empty list raises ValueError.",
        "params": ["numbers"],
        "examples": [_example("[3, 9, 4]", "[3, 9, 4]"), _example("negatives", "[-5, -1, -3]"),
                     _example("empty list", "[]"), _example("mixed types", '[1, "a"]')],
    },
    {
        "name": "get_price", "group": "Data types", "type": "Dictionary",
        "spec": "Return the price of item. A missing item raises KeyError.",
        "params": ["prices", "item"],
        "examples": [_example("apple", '{"apple": 1.5, "bread": 2}', '"apple"'),
                     _example("free item", '{"gift": 0}', '"gift"'),
                     _example("missing item", '{"apple": 1.5}', '"milk"')],
    },
    {
        "name": "swap", "group": "Data types", "type": "Tuple",
        "spec": "Return the two values swapped. Not exactly 2 values raises ValueError.",
        "params": ["pair"],
        "examples": [_example("[1, 2]", "[1, 2]"), _example("[\"a\", \"b\"]", '["a", "b"]'),
                     _example("3 values", "[1, 2, 3]")],
    },
    {
        "name": "common_items", "group": "Data types", "type": "Set",
        "spec": "Return the items found in both sets. Lists you type are turned into sets.",
        "params": ["set_a", "set_b"],
        "examples": [_example("overlap", "[1, 2, 3]", "[2, 3, 4]"),
                     _example("disjoint", "[1, 2]", "[3, 4]"),
                     _example("numbers (wrong type)", "5", "3")],
    },
    {
        "name": "is_leap_year", "group": "Data types", "type": "Date",
        "spec": "True if year is a leap year. A year below 1 raises ValueError.",
        "params": ["year"],
        "examples": [_example("2000", "2000"), _example("1900", "1900"),
                     _example("2024", "2024"), _example("0 (error)", "0")],
    },
    {
        "name": "to_int", "group": "Data types", "type": "Type conversion",
        "spec": "Convert value to int. A bool raises TypeError.",
        "params": ["value"],
        "examples": [_example("\"42\"", '"42"'), _example("-3.9", "-3.9"),
                     _example("true (error)", "true"), _example("\"abc\" (error)", '"abc"')],
    },
    {
        "name": "divide", "group": "Mathematics", "type": "Math",
        "spec": "Return a / b. Dividing by zero raises ZeroDivisionError.",
        "params": ["a", "b"],
        "examples": [_example("10 / 4", "10", "4"), _example("1 / 3", "1", "3"),
                     _example("5 / 0 (error)", "5", "0")],
    },
    {
        "name": "power", "group": "Mathematics", "type": "Math",
        "spec": "Return base raised to exponent.",
        "params": ["base", "exponent"],
        "examples": [_example("2 ** 10", "2", "10"), _example("2 ** -1", "2", "-1"),
                     _example("0 ** -1 (error)", "0", "-1")],
    },
    {
        "name": "square_root", "group": "Mathematics", "type": "Math",
        "spec": "Return the square root of x. A negative x raises ValueError.",
        "params": ["x"],
        "examples": [_example("16", "16"), _example("2", "2"), _example("-4 (error)", "-4")],
    },
    {
        "name": "factorial", "group": "Mathematics", "type": "Math",
        "spec": "Return n factorial. A negative n raises ValueError.",
        "params": ["n"],
        "examples": [_example("0", "0"), _example("10", "10"), _example("-1 (error)", "-1")],
    },
    {
        "name": "average", "group": "Mathematics", "type": "Math",
        "spec": "Return the average of a list. An empty list raises ValueError.",
        "params": ["numbers"],
        "examples": [_example("[1, 2, 3, 4]", "[1, 2, 3, 4]"), _example("floats", "[0.1, 0.2]"),
                     _example("empty list", "[]")],
    },
]

FUNCTIONS_BY_NAME = {item["name"]: item for item in FUNCTIONS}

# The demo shows very large numbers as text, so keep them to a size that is safe to print.
MAX_FACTORIAL_N = 1000
MAX_RESULT_DIGITS = 4000


def parse_input(raw):
    """Turn what the user typed into a Python value.

    Valid JSON becomes a value (18, 3.5, true, null, [1, 2], {"a": 1}, NaN).
    Anything that is not valid JSON is used as plain text.
    """
    if not isinstance(raw, str):
        return raw
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def prepare_arguments(name, values):
    """Convert JSON-style values into the Python types a function expects."""
    if name == "swap" and isinstance(values[0], list):
        return [tuple(values[0])]
    if name == "common_items":
        return [set(v) if isinstance(v, list) else v for v in values]
    return values


def demo_limit_message(name, values):
    """Return a message when an input would produce an unreasonably large number."""
    if name == "factorial":
        n = values[0]
        if isinstance(n, int) and not isinstance(n, bool) and n > MAX_FACTORIAL_N:
            return f"n is limited to {MAX_FACTORIAL_N} in this demo"
    if name == "power":
        base, exponent = values
        numbers = (int, float)
        if (isinstance(base, numbers) and isinstance(exponent, numbers)
                and not isinstance(base, bool) and not isinstance(exponent, bool)
                and isinstance(base, int) and isinstance(exponent, int)
                and exponent > 0 and abs(base) > 1):
            if exponent * math.log10(abs(base)) > MAX_RESULT_DIGITS:
                return "this result has too many digits for the demo"
    return None


def describe_error(error):
    if isinstance(error, KeyError) and error.args:
        return str(error.args[0])
    return str(error)


@app.get("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")


@app.get("/health")
def health():
    return jsonify(status="ok", sha=get_commit_sha())


@app.get("/api/functions")
def list_functions():
    return jsonify(functions=FUNCTIONS)


@app.post("/api/call")
def call_function():
    body = request.get_json(silent=True) or {}
    name = body.get("function")
    inputs = body.get("inputs")

    spec = FUNCTIONS_BY_NAME.get(name)
    if spec is None:
        return jsonify(ok=False, error_type="BadRequest",
                       message=f"unknown function: {name}"), 400
    if not isinstance(inputs, list) or len(inputs) != len(spec["params"]):
        expected = ", ".join(spec["params"])
        return jsonify(ok=False, error_type="BadRequest",
                       message=f"{name} needs {len(spec['params'])} input(s): {expected}"), 400

    values = [parse_input(raw) for raw in inputs]
    shown = ", ".join(repr(v) for v in values)

    limit = demo_limit_message(name, values)
    if limit:
        return jsonify(ok=False, call=f"{name}({shown})", error_type="DemoLimit",
                       message=limit)

    try:
        result = getattr(target, name)(*prepare_arguments(name, values))
        return jsonify(ok=True, call=f"{name}({shown})", result=repr(result),
                       result_type=type(result).__name__)
    except Exception as error:  # every error from target.py is shown, not hidden
        return jsonify(ok=False, call=f"{name}({shown})",
                       error_type=type(error).__name__, message=describe_error(error))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
