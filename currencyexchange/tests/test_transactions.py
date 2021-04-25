from currencyexchange.database.fxrates import FxRate

from .utils import TestCase, create_test_user
from currencyexchange import db


class TrasactionsTest(TestCase):
    def test_inter_account_transfer(self):
        user1 = create_test_user(db.session, balance=500, currency='KES')
        user2 = create_test_user(db.session, balance=750, currency='UGX')
        ug_rate = FxRate(base_currency_code='USD', target_currency_code='UGX',
                         rate=3000)
        ke_rate = FxRate(base_currency_code='USD', target_currency_code='KES',
                         rate=100)
        db.session.add_all([ke_rate, ug_rate])
        db.session.commit()
        from currencyexchange.database.transactions import Transaction
        Transaction.interaccount(sender=user1, recipient=user2, amount=300)
        db.session.refresh(user1)
        db.session.refresh(user2)
        self.assertEqual(user1.account_balance, 200)
