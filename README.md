<p align="center">
  <img src="docs/assets/screens/root.png" alt="socksmith running" width="900">
</p>

<h1 align="center">socksmith</h1>

<p align="center"><b>A Shadowsocks panel with per-user ports, quotas and real traffic accounting.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/socksmith/actions/workflows/ci.yml"><img src="https://github.com/scar8969/socksmith/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-23%20passed-2ea44f" alt="tests: 23 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-66.0%-yellow" alt="coverage: 66.0%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20live-0969da" alt="routes: 10 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

socksmith manages Shadowsocks accounts on one host: each user gets a port, a method, a password and a rate limit, traffic is synced from the node, and a subscription endpoint hands clients their configuration.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

Running a proxy for a handful of people turns into a spreadsheet: who has which port, how much they moved, who is over quota. This service keeps that in a database, exposes it as JSON and as a panel, and keeps the subscription link stable when a port changes.

## What it does

| Capability | How it works |
| --- | --- |
| **Per-user ports and methods** | Each account owns its port, cipher and rate limit; the panel and the API edit the same row. |
| **Traffic sync** | POST /api/traffic ingests node counters and rolls them into per-user totals and quota checks. |
| **Subscription endpoint** | GET /api/subscribe returns a client-ready configuration for the authenticated user. |
| **Admin analytics** | Per-user usage and node totals behind an admin guard. |

## Quickstart

```sh
git clone https://github.com/scar8969/socksmith.git
cd socksmith
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

It is up when this answers:

```sh
curl -s http://127.0.0.1:8000/api/subscribe
```

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/admin.png" alt="/admin" width="100%"><br><sub><code>/admin</code> &middot; 40.9 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/login.png" alt="/login" width="100%"><br><sub><code>/login</code> &middot; 28.1 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/logout.png" alt="/logout" width="100%"><br><sub><code>/logout</code> &middot; 40.9 KB</sub></td>
</tr>
</table>

The other 5 captures — the health, liveness, readiness, metrics and version endpoints — are committed in the same folder rather than shown here.

## API

Every route below is declared in [`openapi/socksmith.yaml`](openapi/socksmith.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/api/subscribe` | subscription |
| `POST` | `/api/traffic` | traffic sync |
| `POST` | `/api/admin/users` | add user |
| `GET` | `/api/admin/analytics` | analytics |
| `GET` | `/api/health` | liveness counters |

## CLI

The same operations without an HTTP client. Installed as `socksmith`, and runnable from a checkout with no install:

```sh
python -m moess.cli --help
```

```text
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
                        http://127.0.0.1:8000)
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |
| `MOESS_DATABASE_URI` | `(empty)` | SQLAlchemy URL for the panel database; defaults to SQLite under the instance dir. |
| `MOESS_SECRET_KEY` | `(empty)` | Flask session key for the panel. Falls back to SECRET_KEY. |
| `MOESS_API_TOKEN` | `(empty)` | Token the CLI sends; the panel checks it on the admin routes. |
| `MOESS_URL` | `http://127.0.0.1:8000` | Base URL the CLI talks to; also accepted as --url. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **23 / 23 passed** (4.0 s, exit 0) |
| Line coverage | **66.0%** — 488 of 702 statements |
| Source | 16 files / 1,566 lines |
| Test code | 4 files / 254 lines |
| Documented paths | 5 in the spec, 3 GET |
| Live probe | 12 GET requests to the booted app, **10 answered 200** |
| Median latency | **41.9 ms** (single uncached request, dev server) |
| Slowest / fastest | 288.0 ms `/` / 21.9 ms `/metrics` |
| Bytes served | 24.5 KB across 12 responses |
| Screenshots | 9 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ moess/app.py:get_app()
                │  reads config once (moess/config.py)
                │  registers the `panel` blueprint
                ▼
           route handler
             ├──▶ moess/models.py        tables, via Flask-SQLAlchemy
             ├──▶ moess/errors.py        raises typed errors → one JSON envelope
             └──▶ moess/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
socksmith/
├── src/moess/
│   ├── http.py                         379  HTTP plumbing for moess: correlation ids, access log
│   ├── config.py                       174  Environment-driven configuration for moess
│   ├── observability.py                169  Structured logging and request correlation for moess
│   ├── cli.py                          148  moeSS CLI - read the panel's counters and call its J
│   ├── models.py                       131  
│   ├── app.py                          120  Application factory for moess
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── panel/api.py                    102  
│   ├── panel/web.py                     54  
│   ├── _app.py                          52  socksmith - application factory
│   ├── paths.py                         52  Filesystem layout for moess
│   ├── seed.py                          27  
├── openapi/socksmith.yaml                 the contract of record
├── schema/socksmith.sql                   the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `panel/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t socksmith .
docker run --rm -p 8000:8000 --env-file .env.example socksmith
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- The service manages configuration and accounting; it does not proxy traffic itself, so a node agent has to report counters.
- Quota enforcement happens at sync time, not per packet.

## License

MIT — see [LICENSE](LICENSE).
