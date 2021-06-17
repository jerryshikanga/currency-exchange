from datetime import datetime
from decimal import Decimal
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

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

    class UserExistsException(Exception):
        """
        Will be riased when trying to add an exisitng user to db
        """
        pass

    def __repr__(self):
        return '<User %r>' % self.name

    @property
    def account_balance_formatted(self):
        return "{} {:.2f}".format(self.default_currency_code,
                                  float(self.account_balance))

    @classmethod
    def create(cls, email, name, password, balance=0, currency='KES'):
        # Check if the user exists in db first
        user = User.query.filter_by(email=email).first()
        if user:
            raise User.UserExistsException

        # Validate the currency code entered by user
        if not Transaction.validate_currency(currency):
            raise Transaction.InvalidCurrencyException

        # create a new user with the form data.
        # Hash the password so the plaintext version isn't saved.
        user = User(email=email, name=name, account_balance=balance,
                    password=generate_password_hash(password, method='sha256'),
                    default_currency_code=currency)

        # add the new user to the database
        db.session.add(user)
        db.session.commit()
        return user

    def update_password(self, new_password):
        self.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        return self

    def update(self, email, name, currency):
        # Check if the email changed and new one already exists
        if email != self.email and User.query.filter_by(email=email).first():
            raise User.UserExistsException

        # check if the user has chnged his/her currency
        # if he has the we have to update his balance too
        if self.default_currency_code != currency:
            # Validate the new currency code entered by user
            if not Transaction.validate_currency(currency):
                raise Transaction.InvalidCurrencyException
            rate = FxRate.get_rate(self.default_currency_code, currency)
            self.account_balance = self.account_balance * rate
            self.default_currency_code = currency
        self.email = email
        self.name = name
        db.session.commit()

    def transact(self, transaction_amount, currency_code, transaction_type,
                 description=None, commit=True):
        rate = FxRate.get_rate(currency_code, self.default_currency_code)
        amount = Decimal(transaction_amount) * rate
        balance_before = self.account_balance if self.account_balance else 0
        if transaction_type == Transaction.Types.Credit:
            self.account_balance += amount
        else:
            if balance_before < amount:
                raise Transaction.InsufficientBalanceException
            self.account_balance -= amount
        # Create transaction for record purposes
        kwargs = dict(
            type=transaction_type, user_id=self.id,
            balance_before=balance_before,
            balance_after=self.account_balance, amount=amount,
            user_currency_code=self.default_currency_code,
            transaction_currency_code=currency_code,
            date_transacted=datetime.now(),
            description=description
            )
        db.session.add(Transaction(**kwargs))
        if commit:
            db.session.commit()
        return kwargs

    def withdraw(self, amount):
        description = f"Withdrawal initiated on {datetime.now()}"
        if amount > self.account_balance:
            raise Transaction.InsufficientBalanceException
        # Add withdrawal logic here

        # Finally debit account
        self.transact(amount, self.default_currency_code,
                      Transaction.Types.Debit,
                      description=description)
