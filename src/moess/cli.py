"""moeSS CLI - read the panel's counters and call its JSON API.

The client half of this tool only needs the standard library, so
`python cli.py --help` works in a bare interpreter with no third-party
packages installed.  The `stats` command opens the SQLite database directly
and therefore imports Flask-SQLAlchemy lazily, inside its handler.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from . import paths

BASE = os.environ.get("MOESS_URL", "http://127.0.0.1:8000")


def _request(path, payload=None, method=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-API-Token"] = token
    req = urllib.request.Request(
        BASE + path, data=data, method=method or ("POST" if data else "GET"), headers=headers
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except urllib.error.URLError as e:
        return 0, json.dumps({"error": "cannot reach %s: %s" % (BASE, e.reason)})


def cmd_health(_args):
    status, body = _request("/api/health")
    print("%s %s" % (status, body))
    return 0 if status == 200 else 1


def cmd_subscribe(args):
    path = "/api/subscribe?token=%s" % args.token
    if args.sub_type:
        path += "&sub_type=%s" % args.sub_type
    status, body = _request(path)
    if status == 200:
        print(body)
    else:
        print("%s %s" % (status, body))
    return 0 if status == 200 else 1


def cmd_report(args):
    status, body = _request(
        "/api/traffic",
        {
            "user_id": args.user_id,
            "node_id": args.node_id,
            "upload": args.upload,
            "download": args.download,
        },
        token=args.token,
    )
    print("%s %s" % (status, body))
    return 0 if status == 200 else 1


def cmd_stats(_args):
    # Offline: read the database the app itself writes, without starting a server.
    sys.path.insert(0, str(paths.PROJECT_ROOT))
    root = str(paths.PROJECT_ROOT)
    instance = str(paths.INSTANCE_DIR)
    paths.ensure_runtime_dirs()
    from flask import Flask

    from .models import Goods, Node, Order, User, db

    app = Flask(__name__, instance_path=instance)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "MOESS_DATABASE_URI", "sqlite:///" + str(paths.INSTANCE_DIR / "moess.db")
    )
    db.init_app(app)
    with app.app_context():
        users = User.query.order_by(User.id).all()
        revenue = sum((o.amount or 0) for o in Order.query.filter_by(status=1).all())
        print("users   %d" % len(users))
        for u in users:
            print(
                "  %-3s %-12s port=%-5s used=%-8.2fGiB admin=%s enable=%s"
                % (
                    u.id,
                    u.username,
                    u.ss_port,
                    u.used_traffic() / 1073741824.0,
                    bool(u.is_admin),
                    bool(u.enable),
                )
            )
        print("nodes   %d" % Node.query.count())
        print("goods   %d" % Goods.query.count())
        print("orders  %d  paid revenue=$%.2f" % (Order.query.count(), revenue))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="moess", description="moeSS panel CLI")
    p.add_argument("--url", help="base URL of a running instance (default $MOESS_URL or %s)" % BASE)
    sub = p.add_subparsers(dest="cmd")

    ph = sub.add_parser("health", help="GET /api/health from a running instance")
    ph.set_defaults(func=cmd_health)

    ps = sub.add_parser("subscribe", help="print a user's subscription config")
    ps.add_argument("token", help="the numeric user id used by /api/subscribe")
    ps.add_argument("--sub-type", dest="sub_type", default="ss", help="ss (default) or clash")
    ps.set_defaults(func=cmd_subscribe)

    pr = sub.add_parser("report", help="POST a traffic sample to /api/traffic")
    pr.add_argument("user_id", type=int)
    pr.add_argument("node_id", type=int)
    pr.add_argument("upload", type=int, help="bytes uploaded since the last report")
    pr.add_argument("download", type=int, help="bytes downloaded since the last report")
    pr.add_argument("--token", required=True, help="value for the X-API-Token header")
    pr.set_defaults(func=cmd_report)

    pt = sub.add_parser("stats", help="counters read straight from the SQLite file")
    pt.set_defaults(func=cmd_stats)
    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    global BASE
    if getattr(args, "url", None):
        BASE = args.url
    if not getattr(args, "cmd", None):
        p.print_help()
        return 0
    return args.func(args)
