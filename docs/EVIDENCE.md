# Evidence

Every line below was produced by a command run against this exact checkout, on this machine, at the time recorded. Nothing here is copied from the README.

| | |
| --- | --- |
| Generated | 2026-10-19 11:53 |
| Python | 3.14.7 |
| Platform | Windows 11 |

## Test suite

```sh
python -m pytest -q
```

- exit code **0**
- 23 passed in 2.18s

## Static gates

| Gate | Exit | Last line |
| --- | --- | --- |
| `ruff check` | 0 | All checks passed! |
| `ruff format --check` | 0 | 21 files already formatted |
| `mypy src` | 0 | Success: no issues found in 17 source files |
| `bandit -c pyproject.toml -r src` | 0 | — |

## Live route walk

The application was imported through `wsgi.py` and each GET path declared in `openapi/` was requested once through the Werkzeug test client.

| Status | Path | Bytes | Content-Type |
| --- | --- | --- | --- |
| 401 | `/api/subscribe` | 27 | application/json |
| 403 | `/api/admin/analytics` | 27 | application/json |
| 200 | `/api/health` | 54 | application/json |

3 paths walked, 0 of them raised or answered 5xx.

## CLI

```
usage: moess [-h] [--url URL] {health,subscribe,report,stats} ...

moeSS panel CLI

positional arguments:
  {health,subscribe,report,stats}
    health              GET /api/health from a running instance
    subscribe           print a user's subscription config
    report              POST a traffic sample to /api/traffic
    stats               counters read straight from the SQLite file

options:
  -h, --help            show this help message and exit
  --url URL             base URL of a running instance (default $MOESS_URL or
```

## Screenshots

Captured from the running service with headless Chromium at 1440x900 and committed with the repository:

| File | Bytes |
| --- | --- |
| `docs/assets/screens/admin.png` | 41,890 |
| `docs/assets/screens/healthz.png` | 8,407 |
| `docs/assets/screens/livez.png` | 7,468 |
| `docs/assets/screens/login.png` | 28,772 |
| `docs/assets/screens/logout.png` | 41,890 |
| `docs/assets/screens/metrics.png` | 19,389 |
| `docs/assets/screens/readyz.png` | 7,880 |
| `docs/assets/screens/root.png` | 41,890 |
| `docs/assets/screens/version.png` | 25,672 |

## What this file does not prove

- It is not a load test: every request is a single uncached call from one process.
- A green suite is not a coverage claim; `pytest --cov` reports the number the README quotes.
- The route walk exercises GET paths only; mutating routes are covered by the suite.
