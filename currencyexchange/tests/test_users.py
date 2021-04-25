from unittest import TestCase

from currencyexchange import create_app, db
from currencyexchange.database.auth import User
from currencyexchange.database.transactions import Transaction
from currencyexchange.tests.utils import create_test_user,\
    delete_all_users, delete_all_transactions


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
        password = 'secret_password'
        user = User.create('myv3@d483.com', 'John Doe', password)
        self.assertEqual(user.account_balance, 0)
        self.assertEqual(user.default_currency_code, 'KES')
        self.assertNotEqual(user.password, password)
        self.assertEqual(user.name, 'John Doe')
        self.assertEqual(user.email, 'myv3@d483.com')

    def test_account_balance_formatting(self):
        user = create_test_user(db.session, currency='USD', balance=546.0)
        expected = f"USD 546.00"
        self.assertEqual(user.account_balance_formatted, expected)

    def test_account_credit_same_currency(self):
        delete_all_users()
        delete_all_transactions()
        user = create_test_user(db.session)
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

    def test_user_update_use_unsupported_currency(self):
        create_test_user(db.session)
        