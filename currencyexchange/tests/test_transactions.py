from currencyexchange.database.auth import User
import pytest
import random

from currencyexchange.database.fxrates import FxRate

from .utils import TestCase, create_test_user
from currencyexchange import db


@pytest.fixture
def test_user():
    username = f"user{random.randint(1, 999)}"
    return User(username=username)


class TrasactionsTest(TestCase):
    def setUp(self) -> None:
        self.user1 = create_test_user(db.session, balance=500, currency='KES')
        self.user2 = create_test_user(db.session, balance=750, currency='UGX')

    def test_inter_account_transfer(self):
        ug_rate = FxRate(base_currency_code='USD', target_currency_code='UGX',
                         rate=3000)
        ke_rate = FxRate(base_currency_code='USD', target_currency_code='KES',
                         rate=100)
        db.session.add_all([ke_rate, ug_rate])
        db.session.commit()
        from currencyexchange.database.transactions import Transaction
        Transaction.interaccount(sender=self.user1, recipient=self.user2,
                                 amount=300)
        db.session.refresh(self.user1)
        db.session.refresh(self.user2)
        self.assertEqual(self.user1.account_balance, 200)

    def test_inter_account_transfer_btn_same_user(self):
        # ug_rate = FxRate(base_currency_code='USD', rate=3000,
        #                  target_currency_code='UGX',)
        # ke_rate = FxRate(base_currency_code='USD', rate=100,
        #                  target_currency_code='KES',)
        # db.session.add_all([ke_rate, ug_rate])
        # db.session.commit()
        from currencyexchange.database.transactions import Transaction
        Transaction.interaccount(sender=self.user1,
                                 recipient=self.user1,
                                 amount=300)
        db.session.refresh(self.user1)
        db.session.refresh(self.user2)
        self.assertEqual(self.user1.account_balance, 500)
