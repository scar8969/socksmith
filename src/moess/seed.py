from .models import GB, Goods, Node, User, db


def seed():
    if User.query.count() == 0:
        admin = User(username="admin", ss_port=1024, is_admin=True)
        admin.set_password("admin123")
        demo = User(username="demo", ss_port=1025)
        demo.set_password("demo123")
        db.session.add_all([admin, demo])
        db.session.add_all(
            [
                Node(name="HK-01", server="hk01.example.com", ss_port=8388, country="HK"),
                Node(name="US-03", server="us03.example.com", ss_port=8388, country="US"),
                Node(name="SG-02", server="sg02.example.com", ss_port=8388, country="SG"),
            ]
        )
        db.session.add_all(
            [
                Goods(name="Trial", transfer=GB, money=0, days=7),
                Goods(name="Starter", transfer=5 * GB, money=2.99, days=30),
                Goods(name="Pro", transfer=50 * GB, money=9.99, days=30),
                Goods(name="Ultimate", transfer=200 * GB, money=19.99, days=90),
            ]
        )
        db.session.commit()
