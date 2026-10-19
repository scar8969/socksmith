import hashlib

from flask_sqlalchemy import SQLAlchemy

from .clock import utcnow

db = SQLAlchemy()
GB = 1024**3


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128), default="")
    ss_port = db.Column(db.Integer, unique=True)
    ss_password = db.Column(db.String(64), default="")
    ss_method = db.Column(db.String(32), default="aes-256-gcm")
    rate_up_mbps = db.Column(db.Integer, default=10)
    rate_down_mbps = db.Column(db.Integer, default=10)
    upload_traffic = db.Column(db.BigInteger, default=0)
    download_traffic = db.Column(db.BigInteger, default=0)
    total_traffic = db.Column(db.BigInteger, default=20 * GB)
    enable = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def set_password(self, raw):
        self.password_hash = _hash(raw, "moess")

    def check_password(self, raw):
        return self.password_hash == _hash(raw, "moess")

    def used_traffic(self):
        return (self.upload_traffic or 0) + (self.download_traffic or 0)

    def overflow(self):
        return self.used_traffic() >= (self.total_traffic or 0)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "ss_port": self.ss_port,
            "rate_up": self.rate_up_mbps,
            "rate_down": self.rate_down_mbps,
            "used": self.used_traffic(),
            "total": self.total_traffic,
            "enable": self.enable,
            "is_admin": self.is_admin,
        }

    def __init__(self, **kw):
        # A column default only materialises at INSERT, so the two values the
        # panel reads before a flush are seeded here as well.
        kw.setdefault("upload_traffic", 0)
        kw.setdefault("download_traffic", 0)
        kw.setdefault("total_traffic", 20 * GB)
        kw.setdefault("ss_port", 8388)
        kw.setdefault("ss_method", "aes-256-gcm")
        kw.setdefault("rate_up_mbps", 10)
        kw.setdefault("rate_down_mbps", 10)
        kw.setdefault("password_hash", "")
        # Everything else - username, ss_password, enable, is_admin - goes
        # straight to the declarative constructor.  The previous hand-rolled
        # version copied a fixed list of keys and silently dropped the rest, so
        # every seeded account came back with username=None, enabling nobody and
        # with is_admin=None, which no admin route accepts.
        super().__init__(**kw)


class Node(db.Model):
    __tablename__ = "nodes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default="")
    server = db.Column(db.String(256), default="")
    ss_port = db.Column(db.Integer, default=8388)
    ss_method = db.Column(db.String(32), default="aes-256-gcm")
    country = db.Column(db.String(8), default="CN")
    used_traffic = db.Column(db.BigInteger, default=0)
    total_traffic = db.Column(db.BigInteger, default=GB)
    enable = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, nullable=True)


class TrafficLog(db.Model):
    __tablename__ = "traffic_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    node_id = db.Column(db.Integer, index=True)
    upload = db.Column(db.BigInteger, default=0)
    download = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)


class InviteCode(db.Model):
    __tablename__ = "invite_codes"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True)
    user_id = db.Column(db.Integer, default=0)
    consumed = db.Column(db.Boolean, default=False)
    consumed_by = db.Column(db.String(64), default="")
    created_at = db.Column(db.DateTime, default=utcnow)


class Goods(db.Model):
    __tablename__ = "goods"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default="")
    content = db.Column(db.String(256), default="")
    transfer = db.Column(db.BigInteger, default=GB)
    money = db.Column(db.Float, default=0)
    level = db.Column(db.Integer, default=0)
    days = db.Column(db.Integer, default=30)
    status = db.Column(db.Integer, default=1)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    goods_id = db.Column(db.Integer, index=True)
    status = db.Column(db.Integer, default=0)
    amount = db.Column(db.Float, default=0)
    out_trade_no = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime, default=utcnow)


def _hash(pw, salt):
    return hashlib.sha256(f"{salt}:{pw}".encode()).hexdigest()
