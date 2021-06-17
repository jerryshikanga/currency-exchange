from mock import patch

from currencyexchange import db
from .utils import TestCase


class UserTests(TestCase):
    def setUp(self):
        from currencyexchange.tests import utils
        utils.delete_all_users()
        utils.delete_all_transactions()

    def test_new_user(self):
        """
        GIVEN a User model
        WHEN a new User is created
        THEN check the email and hashed_password fields are defined correctly
        """
        from currencyexchange.tests.utils import create_test_user
        password = 'secret_password'
        user = create_test_user(db.session, email='myv3@d483.com',
                                password=password)
        self.assertEqual(user.account_balance, 0)
        self.assertEqual(user.default_currency_code, 'KES')
        self.assertNotEqual(user.password, password)
        self.assertEqual(user.name, 'John Doe')
        self.assertEqual(user.email, 'myv3@d483.com')

    def test_account_balance_formatting(self):
        """
        GIVEN a User model
        WHEN a balance is accessed
        THEN it should be returned in the curreny amount.decimal format
        """
        from currencyexchange.tests.utils import create_test_user
        user = create_test_user(db.session, currency='USD', balance=546.0)
        expected = "USD 546.00"
        self.assertEqual(user.account_balance_formatted, expected)

    def test_account_credit_same_currency(self):
        from currencyexchange.tests.utils import create_test_user
        from currencyexchange.database.transactions import Transaction
        user = create_test_user(db.session)
        self.assertEqual(user.account_balance, 0)
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
        from currencyexchange.tests.utils import create_test_user
        from currencyexchange.database.transactions import Transaction
        user = create_test_user(db.session)
        with self.assertRaises(Transaction.InvalidCurrencyException):
            user.update(user.email, user.name, 'K123')

    @patch("currencyexchange.database.fxrates.FxRate.get_rate")
    def test_user_currency_update_update_balance_too(self, mock_get_rate):
        mock_get_rate.return_value = 100
        from currencyexchange.tests.utils import create_test_user
        user = create_test_user(db.session, balance=1, currency='USD')
        self.assertEqual(user.account_balance, 1)
        user.update("newemail@domain.com", "New John", "KES")
        db.session.refresh(user)
        self.assertEqual(user.default_currency_code, "KES")
        self.assertEqual(user.account_balance, 100)

    def test_cannot_debit_less_than_balance(self):
        from currencyexchange.tests.utils import create_test_user
        from currencyexchange.database.transactions import Transaction
        user = create_test_user(db.session, balance=125, currency='KES')
        initial_balance = user.account_balance
        with self.assertRaises(Transaction.InsufficientBalanceException):
            user.transact(525, 'KES', Transaction.Types.Debit)
            self.assertEqual(user.account_balance, initial_balance)
