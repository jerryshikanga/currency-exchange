from currencyexchange import db
from currencyexchange.database.fxrates import FxRate
from currencyexchange.database.transactions import Transaction
from currencyexchange.database.auth import User


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


def delete_all_users():
    db.session.query(User).delete()
    db.session.commit()


def delete_all_transactions():
    db.session.query(Transaction).delete()
    db.session.commit()


def delete_all_rates():
    db.session.query(FxRate).delete()
    db.session.commit()
