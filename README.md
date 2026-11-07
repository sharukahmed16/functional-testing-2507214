# functional-testing-2507214

![CI](https://github.com/sharukahmed16/functional-testing-2507214/actions/workflows/ci.yml/badge.svg)

Functional tests, CI/CD and live deployment for `target.py` (16 functions).
Course: Software Quality Assurance, MIT. Author: Sakib (2507214).

- **Live site:** https://functional-testing-2507214.onrender.com
- **Health check (shows deployed commit SHA):** https://functional-testing-2507214.onrender.com/health
- **Demo video:** PASTE_YOUR_VIDEO_LINK_HERE

## What is in this repository

| Path | Purpose |
|------|---------|
| `target.py` | The 16 functions under test (never modified) |
| `tests/test_target.py` | Functional tests for all 16 functions (Part 1) |
| `tests/test_app.py` | Tests for the web app and the `/health` endpoint |
| `app.py`, `static/index.html` | Flask backend and web frontend (Part 4) |
| `.github/workflows/ci.yml` | Test, deploy and smoke-test pipeline (Parts 3 and 5) |
| `scripts/smoke_test.py` | Waits for the new commit on the live site, then makes three live requests |
| `requirements.txt` | Pinned dependencies |

## Setup

```bash
git clone https://github.com/sharukahmed16/functional-testing-2507214.git
cd functional-testing-2507214
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the tests

```bash
pytest --cov=target --cov-branch --cov-report=term-missing
```

The CI pipeline adds `--cov-fail-under=100`, so the build fails if line or branch coverage of
`target.py` drops below 100%. Lint with `flake8 .`.

## Run the web app locally

```bash
python app.py
# open http://127.0.0.1:5000
```

Type the inputs for any function and the page shows the value it returns or the exception
it raises. Inputs are read as JSON (`18`, `3.5`, `true`, `null`, `[1, 2, 3]`, `{"a": 1}`);
text that is not valid JSON is used as a plain string.

## How testing works (Part 1)

Every function has tests for valid inputs, boundary values, invalid values and wrong types.
Tests use `pytest.mark.parametrize`, `pytest.raises` with the exact exception class
(and `match=` for messages), and check result types with a small `assert_same` helper.
`pytest.approx` is used only for inexact floating point results. There are no `skip` or `xfail`
markers. Result: 100% line and branch coverage of `target.py`.

## CI/CD pipeline (Parts 3 and 5)

```
push / PR  ->  test (3.10, 3.11, 3.12: flake8 + pytest + 100% coverage)
                 |
                 +-- only on push to main, after all tests pass -->
                       deploy (calls Render deploy hook for this exact commit)
                         |
                         +--> smoke-test (waits for /health to show the new SHA,
                                          then makes 3 live requests)
```

- Auto-deploy is **off** on the host, so only the `deploy` job can publish code.
- `deploy` has `needs: test` and runs only for pushes to `main`.
- `/health` returns `{"status": "ok", "sha": "<commit>"}` and the page footer shows the same SHA.
- The coverage report (`coverage.xml` and `htmlcov/`) is uploaded as an artifact on every run.

Required repository secrets (Settings, Secrets and variables, Actions):

| Secret | Value |
|--------|-------|
| `RENDER_DEPLOY_HOOK_URL` | Deploy hook URL from the Render service settings |
| `LIVE_URL` | Public URL of the site, for example `https://functional-testing-2507214.onrender.com` |

## Suspected bugs in target.py

`target.py` was not modified. These are behaviours that look wrong or surprising compared with
the description of each function. Tests were written against the current behaviour where it is
well defined, and the points below are not hidden by any `skip` or `xfail`.

| # | Function | Observation |
|---|----------|-------------|
| 1 | `greet` | A non-string name such as `123` raises `AttributeError` (from `.strip()`), not a clear `TypeError` like `count_vowels` and `invert` do. |
| 2 | `common_items` | No type check. `common_items(5, 3)` returns `1` (a bitwise AND), and booleans behave the same way. Lists raise `TypeError` only by accident. |
| 3 | `power` | `power(-8, 0.5)` returns a complex number instead of raising an error. |
| 4 | `is_adult`, `celsius_to_fahrenheit`, `factorial` | `bool` is accepted as a number (`factorial(True)` is `1`, `celsius_to_fahrenheit(True)` is `33.8`). `is_adult(float("nan"))` quietly returns `False`. |
| 5 | `find_max` | With NaN the result depends on order: `find_max([nan, 1])` is `nan` but `find_max([1, nan])` is `1`. |
| 6 | `swap` | Accepts any sized object: `swap("ab")` returns `("b", "a")`, and `swap({1: 2, 3: 4})` fails with `KeyError: 0`. |
| 7 | `is_leap_year` | Non-integer years are accepted: `is_leap_year(2000.0)` is `True` and `is_leap_year(1.5)` is `False`. |
| 8 | `average` | `average([1e308, 1e308])` returns `inf` because the sum overflows, although the true average is `1e308`. |

## Commit and branch workflow

Work was done on feature branches (`feature/functional-tests`, `feature/web-app`,
`feature/ci-pipeline`) and merged into `main` with pull requests. `main` is protected and
requires the `test` checks to pass.
