from flask_login import UserMixin

from currencyexchange import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    # profile_picture
    default_currency_code = db.Column(db.String(3))
    account_balance = db.Column(db.Float(precision=2, asdecimal=True))

    def __repr__(self):
        return '<User %r>' % self.name
