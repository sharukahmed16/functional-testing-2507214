"""Tests for the Flask app: /health, the page and the /api/call endpoint."""

import pytest

import app as app_module


@pytest.fixture()
def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def call(client, function, *inputs):
    return client.post("/api/call", json={"function": function, "inputs": list(inputs)})


def test_health_returns_commit_sha(client, monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abc123def456")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "sha": "abc123def456"}


def test_health_uses_fallback_variables(client, monkeypatch):
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    monkeypatch.delenv("RAILWAY_GIT_COMMIT_SHA", raising=False)
    monkeypatch.setenv("COMMIT_SHA", "from-env")
    assert client.get("/health").get_json()["sha"] == "from-env"
    monkeypatch.delenv("COMMIT_SHA")
    assert client.get("/health").get_json()["sha"] == "unknown"


def test_home_page_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"target.py test bench" in response.data
    assert b'id="sha"' in response.data


def test_function_list_covers_all_sixteen(client):
    names = [item["name"] for item in client.get("/api/functions").get_json()["functions"]]
    assert len(names) == 16
    assert names[0] == "is_adult"
    assert names[-1] == "average"


def test_every_listed_example_runs(client):
    for item in client.get("/api/functions").get_json()["functions"]:
        for example in item["examples"]:
            response = call(client, item["name"], *example["inputs"])
            assert response.status_code == 200, (item["name"], example)


@pytest.mark.parametrize(
    "function, inputs, result, result_type",
    [
        ("is_adult", ["20"], "True", "bool"),
        ("divide", ["10", "4"], "2.5", "float"),
        ("count_vowels", ["Hello World"], "3", "int"),
        ("greet", ["null"], "'Hello, Guest!'", "str"),
        ("swap", ["[1, 2]"], "(2, 1)", "tuple"),
        ("common_items", ["[1, 2, 3]", "[2, 3, 4]"], "{2, 3}", "set"),
        ("get_price", ['{"apple": 1.5}', '"apple"'], "1.5", "float"),
        ("factorial", ["5"], "120", "int"),
    ],
)
def test_successful_calls(client, function, inputs, result, result_type):
    data = call(client, function, *inputs).get_json()
    assert data["ok"] is True
    assert data["result"] == result
    assert data["result_type"] == result_type


@pytest.mark.parametrize(
    "function, inputs, error_type",
    [
        ("divide", ["1", "0"], "ZeroDivisionError"),
        ("is_adult", ["-1"], "ValueError"),
        ("is_adult", ['"18"'], "TypeError"),
        ("get_price", ['{"a": 1}', '"b"'], "KeyError"),
        ("swap", ["[1, 2, 3]"], "ValueError"),
        ("to_int", ["true"], "TypeError"),
    ],
)
def test_function_errors_are_reported(client, function, inputs, error_type):
    response = call(client, function, *inputs)
    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is False
    assert data["error_type"] == error_type


def test_key_error_message_has_no_extra_quotes(client):
    data = call(client, "get_price", '{"a": 1}', '"milk"').get_json()
    assert data["message"] == "milk not found"


def test_plain_text_is_used_as_string(client):
    data = call(client, "count_vowels", "banana").get_json()
    assert data["result"] == "3"


def test_unknown_function_is_rejected(client):
    response = call(client, "os_system", "x")
    assert response.status_code == 400
    assert response.get_json()["error_type"] == "BadRequest"


def test_wrong_number_of_inputs_is_rejected(client):
    response = call(client, "divide", "1")
    assert response.status_code == 400
    assert "2 input(s)" in response.get_json()["message"]


def test_missing_body_is_rejected(client):
    assert client.post("/api/call").status_code == 400


def test_large_inputs_hit_the_demo_limit(client):
    for function, inputs in [("factorial", ["100000"]), ("power", ["10", "100000"])]:
        data = call(client, function, *inputs).get_json()
        assert data["ok"] is False
        assert data["error_type"] == "DemoLimit"


def test_boolean_and_float_powers_are_not_limited(client):
    assert call(client, "power", "true", "100000").get_json()["ok"] is True
    assert call(client, "power", "2.0", "10").get_json()["result"] == "1024.0"
