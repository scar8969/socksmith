from ..models import Goods, Node, Order, User
from .api import _current_user

from flask import Blueprint, render_template, redirect, url_for, session, flash, request as _req

web = Blueprint("web", __name__)

@web.route("/")
def index():
    # "/" is the one entry page.  It renders index.html with the rows the
    # database actually holds: the plans on offer for a visitor, and the signed-in
    # account's own quota, ports and subscription URL.  There is deliberately no
    # second dashboard template - a duplicate page would only be a place for the
    # two views to drift apart.
    return render_template("index.html",
                           user=_current_user(),
                           nodes=Node.query.order_by(Node.id).all(),
                           goods=Goods.query.filter_by(status=1).order_by(Goods.id).all())

@web.route("/login", methods=["GET", "POST"])
def login():
    if _req.method == "POST":
        u = User.query.filter_by(username=_req.form.get("username", "")).first()
        if u and u.check_password(_req.form.get("password", "")):
            session["user_id"] = u.id
            return redirect(url_for("web.index"))
        flash("Invalid username or password", "error")
    return render_template("login.html")

@web.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("web.index"))

@web.route("/admin")
def admin():
    if not (_u := _current_user()) or not _u.is_admin:
        return redirect(url_for("web.index"))
    return render_template("admin.html", user=_u,
                           users=User.query.order_by(User.id).all(),
                           nodes=Node.query.order_by(Node.id).all(),
                           goods=Goods.query.order_by(Goods.id).all(),
                           orders=Order.query.order_by(Order.id).all())
