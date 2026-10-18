<p align="center">
  <img src="docs/assets/screens/root.png" alt="socksmith running" width="900">
</p>

<h1 align="center">socksmith</h1>

<p align="center"><b>A Shadowsocks panel with per-user ports, quotas and real traffic accounting.</b></p>

<p align="center">
  <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-23%20passed-2ea44f" alt="tests: 23 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-66.0%-yellow" alt="coverage: 66.0%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20answered-0969da" alt="routes: 10 answered"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

socksmith manages Shadowsocks accounts on one host: each user gets a port, a method, a password and a rate limit, traffic is synced from the node, and a subscription endpoint hands clients their configuration.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

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

The same work from the CLI:

```sh
python -m moess.cli --help
```

Commands: `health`, `subscribe`, `report`, `stats`.

A first request:

```sh
curl -s http://127.0.0.1:8000/api/subscribe | head
```

## Requirements

- Python **3.11+** — CI runs 3.11, 3.12 and 3.13.
- Runtime dependencies: `Flask>=3.0`, `Flask-SQLAlchemy>=3.1`, `SQLAlchemy>=2.0`, `PyYAML>=6.0`.
- No JavaScript build step: every page is server-rendered Jinja.

## API

Every route below is in [`openapi/socksmith.yaml`](openapi/socksmith.yaml) and is exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/api/subscribe` | subscription |
| `POST` | `/api/traffic` | traffic sync |
| `POST` | `/api/admin/users` | add user |
| `GET` | `/api/admin/analytics` | analytics |
| `GET` | `/api/health` | liveness counters |

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

## Measured, not estimated

These numbers were produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **23 / 23 passed** (4.0 s, exit 0) |
| Line coverage | **66.0%** — 488 of 702 statements |
| Source | 16 files / 1,544 lines |
| Test code | 4 files / 254 lines |
| Documented paths | 5 in the spec, 3 GET |
| Live probe | 12 GET requests to the booted app, **10 answered 200** |
| Median latency | **41.9 ms** (single uncached request, dev server) |
| Slowest / fastest | 288.0 ms `/` / 21.9 ms `/metrics` |
| Bytes served | 24.5 KB across 12 responses |
| Screenshots | 9 captured |

## Architecture

```
socksmith/
├── src/moess/
│   ├── http.py                         379  HTTP plumbing for moess: correlation ids, access log
│   ├── config.py                       175  Environment-driven configuration for moess
│   ├── observability.py                169  Structured logging and request correlation for moess
│   ├── cli.py                          144  moeSS CLI - read the panel's counters and call its J
│   ├── models.py                       130  
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
| Coverage | `pytest --cov` | floor set in `pyproject.toml` from the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 for every push to `main`, plus a container build. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Deploy

```sh
docker build -t socksmith .
docker run --rm -p 8000:8000 --env-file .env.example socksmith
```

Configuration is environment-only — every variable is documented in [`.env.example`](.env.example), and the service refuses to start with a production secret missing.

## Limits, stated rather than hidden

- The service manages configuration and accounting; it does not proxy traffic itself, so a node agent has to report counters.
- Quota enforcement happens at sync time, not per packet.

## License

MIT — see [LICENSE](LICENSE).
