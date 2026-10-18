"""socksmith - application factory.

Templates live in the project-root templates/ directory, so the template folder is passed
explicitly: Flask(__name__) alone would look in /templates, and the SQLite file is pinned to
the project-root instance/ directory for the same reason.

panel/api.py declares its own "/api/..." paths, so the blueprint is registered WITHOUT a
url_prefix. Passing url_prefix="/api" published the broken double prefix /api/api/... and
made GET /api/subscribe unreachable (404) while /api/api/admin/analytics answered 403.
"""

import os

from . import paths
from .models import db
from .panel.api import bp
from .panel.web import web
from .seed import seed

paths.ensure_runtime_dirs()

APP_NAME = "\u26a1 moeSS"


def build_app():
    from flask import Flask

    app = Flask(
        __name__, template_folder=str(paths.TEMPLATES_DIR), instance_path=str(paths.INSTANCE_DIR)
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "MOESS_DATABASE_URI", "sqlite:///" + str(paths.INSTANCE_DIR / "moess.db")
    )
    app.config["SECRET_KEY"] = os.environ.get("MOESS_SECRET_KEY", "dev-secret-key")
    app.config["API_TOKEN"] = os.environ.get("MOESS_API_TOKEN", "dev-api-token")
    db.init_app(app)
    app.register_blueprint(bp)
    app.register_blueprint(web)

    @app.context_processor
    def _brand():
        """base.html renders the brand and page titles from app_name."""
        return {"app_name": APP_NAME}

    with app.app_context():
        db.create_all()
        seed()
    return app


app = build_app()
