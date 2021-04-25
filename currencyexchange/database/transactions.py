from currencyexchange import db


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance_before = db.Column(
        db.Float(precision=2, asdecimal=True), nullable=False)
    balance_after = db.Column(
        db.Float(precision=2, asdecimal=True), nullable=False)
    amount = db.Column(
        db.Float(precision=2, asdecimal=True), nullable=False)
    user_currency_code = db.Column(db.String(3), nullable=False)
    transaction_currency_code = db.Column(
        db.String(3), index=True, nullable=False)
    date_transacted = db.Column(db.DateTime(), index=True, nullable=False)
    description = db.Column(db.String(255))

    class Types:
        Debit = 'Debit'
        Credit = 'Credit'

    def __repr__(self) -> str:
        return f"{self.transaction_currency_code} {self.amount} {self.user.name}"
