import os
import json
from decimal import Decimal
from unittest import TestCase

from requests import Response
from mock import patch

from currencyexchange import db
from currencyexchange.database.fxrates import FxRate
from currencyexchange.database.transactions import Transaction
from currencyexchange.database.auth import User
from currencyexchange import create_app


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


class UserTests(TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        ctx = self.app.app_context()
        ctx.push()
        return super().setUp()

    def test_new_user(self):
        """
        GIVEN a User model
        WHEN a new User is created
        THEN check the email and hashed_password fields are defined correctly
        """
        delete_all_users()
        user = User(name='John Doe', email='test1@domain.com')
        # self.assertEqual(user.account_balance, 0)

    def test_account_credit_same_currency(self):
        delete_all_users()
        delete_all_transactions()
        user = User(name='John Doe', email='test2@domain.com')
        db.session.add_all([user,])
        db.session.commit()
        user.transact(5, 'KES', Transaction.Types.Credit)
        db.session.refresh(user)
        self.assertEqual(user.account_balance, 5)
        query = Transaction.query.filter_by(user_id=user.id)
        self.assertEqual(query.count(), 1)
        trxn = query.first()
        self.assertEqual(trxn.balance_before, 0)
        self.assertEqual(trxn.balance_after, 5)
        self.assertEqual(trxn.amount, 5)
        self.assertEqual(trxn.user_currency_code, 'KES')
        self.assertEqual(trxn.transaction_currency_code, 'KES')


def delete_all_rates():
    db.session.query(FxRate).delete()
    db.session.commit()


class FxRateTests(TestCase):
    def setUp(self) -> None:
        os.environ['FIXER_SECRET_KEY'] = 'test'
        self.app = create_app()
        ctx = self.app.app_context()
        ctx.push()
        return super().setUp()

    @patch('currencyexchange.database.fxrates.requests.get')
    def test_rates_retrieval(self, mock_requests):
        delete_all_rates()
        expected_response = {
            "success": True,
            "timestamp": 1619062744,
            "base": "EUR",
            "date": "2021-04-22",
            "rates": {
                "AED": 4.422861,
                "AFN": 93.376639,
                "ALL": 123.238632,
                "AMD": 628.811549,
                "ANG": 2.161392,
                "AOA": 793.029331,
                "ARS": 111.926674,
                "AUD": 1.552483,
                "AWG": 2.167663,
                "AZN": 2.040164,
                "BAM": 1.960927,
                "BBD": 2.43119
            }
        }
        mock_requests.return_value = MockResponse(json.dumps(expected_response))
        FxRate.refresh_from_api()
        aed = FxRate.query.filter_by(target_currency_code='AED').first()
        self.assertAlmostEqual(aed.rate, Decimal(expected_response['rates']['AED']))
        expected_updated_response = {
            "success": True,
            "timestamp": 1619062744,
            "base": "EUR",
            "date": "2021-04-22",
            "rates": {
                "AED": 16.422861,
                "AFN": 93.376639,
            }
        }
        mock_requests.return_value = MockResponse(json.dumps(expected_updated_response))
        FxRate.refresh_from_api()
        db.session.refresh(aed)
        self.assertAlmostEqual(aed.rate, Decimal(expected_updated_response['rates']['AED']))

    def test_rate_conversion(self):
        delete_all_rates()
        kes_rate = FxRate(target_currency_code='KES', rate=100)
        ugx_rate = FxRate(target_currency_code='UGX', rate=3000)
        db.session.add_all([kes_rate, ugx_rate])
        db.session.commit()
        kes_to_ugx = FxRate.get_rate('KES', 'UGX')
        self.assertEqual(kes_to_ugx, 30)
