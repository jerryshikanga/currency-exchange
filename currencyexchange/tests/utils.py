from datetime import datetime
import random
from unittest import TestCase as InternalTestCase

from werkzeug.security import generate_password_hash

from currencyexchange import db, create_app


class MockResponse(object):
    def __init__(self, text, status_code=200, headers=None, *args, **kwargs):
        self.text = text
        self.headers = headers
        self.status_code = status_code

    def json(self):
        import json
        return json.loads(self.text)

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def message(self):
        return self.text

    @property
    def reason(self):
        return self.text


class TestCase(InternalTestCase):
    def setUp(self) -> None:
        self.app = create_app()
        ctx = self.app.app_context()
        ctx.push()
        return super().setUp()


def delete_all_users():
    from currencyexchange.database.auth import User
    db.session.query(User).delete()
    db.session.commit()


def delete_all_transactions():
    from currencyexchange.database.transactions import Transaction
    db.session.query(Transaction).delete()
    db.session.commit()


def delete_all_rates():
    from currencyexchange.database.fxrates import FxRate
    db.session.query(FxRate).delete()
    db.session.commit()


def create_test_user(db_session, name='John Doe', email=None, balance=0, currency='KES', password='password'):
    if email is None:
        random.seed(datetime.now())
        u_code = random.randint(1, 999)
        d_code = random.randint(1000, 9999)
        email = f"testuser{u_code}@domain_{d_code}.com"
    from currencyexchange.database.auth import User
    password=generate_password_hash(password, method='sha256')
    user = User(name=name, email=email, account_balance=balance, 
                default_currency_code=currency, password=password)
    db_session.add(user)
    db_session.commit()
    return user
