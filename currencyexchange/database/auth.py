from datetime import datetime
from decimal import Decimal
from flask_login import UserMixin

from currencyexchange import db
from currencyexchange.database.fxrates import FxRate
from currencyexchange.database.transactions import Transaction


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    last_updated = db.Column(db.DateTime())
    # profile_picture
    default_currency_code = db.Column(db.String(3), default='KES')
    account_balance = db.Column(
        db.Float(precision=2, asdecimal=True),
        default=0, )
    transactions = db.relationship('Transaction', backref='user',
                                   lazy='joined')

    def __repr__(self):
        return '<User %r>' % self.name

    def transact(self, transaction_amount, currency_code, transaction_type,
                 description=None, commit=True):
        rate = FxRate.get_rate(currency_code, self.default_currency_code)
        amount = Decimal(transaction_amount) * rate
        balance_before = self.account_balance if self.account_balance else 0
        self.account_balance += amount
        # create transaction
        kwargs = dict(
            type=transaction_type, user_id=self.id,
            balance_before=balance_before,
            balance_after=self.account_balance, amount=amount,
            user_currency_code=self.default_currency_code,
            transaction_currency_code=currency_code,
            date_transacted=datetime.now(),
            )
        db.session.add(Transaction(**kwargs))
        if commit:
            db.session.commit()
        return kwargs
