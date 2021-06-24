import datetime
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

    supported_currencies = [
        'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA',
        'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD',
        'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP',
        'BYN', 'BYR', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP', 'CNY',
        'COP', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP',
        'DZD', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL',
        'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL',
        'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 'IRR',
        'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF',
        'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
        'LSL', 'LTL', 'LVL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK',
        'MNT', 'MOP', 'MRO', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN',
        'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN',
        'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB',
        'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLL',
        'SOS', 'SRD', 'STD', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT',
        'TND', 'TOP', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD',
        'UYU', 'UZS', 'VEF', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU',
        'XCD', 'XDR', 'XOF', 'XPF', 'YER', 'ZAR', 'ZMK', 'ZMW', 'ZWL'
    ]

    supported_deposit_withdrawal_currencies = ['KES', 'UGX', 'TZS']

    @classmethod
    def validate_currency(cls, code):
        return code in Transaction.supported_currencies

    @classmethod
    def validate_withdrawal_deposit_currency(cls, code):
        return code in Transaction.supported_deposit_withdrawal_currencies

    class Types:
        Debit = 'Debit'
        Credit = 'Credit'
        Withdrawal = 'Withdrawal'
        Deposit = 'Deposit'

    @property
    def formatted_date(self):
        fmt = "%d-%m-%Y %H:%M"
        return datetime.datetime.strftime(self.date_transacted, fmt)

    @property
    def balance_before_formatted(self):
        return "{:.2f}".format(float(self.balance_before))

    @property
    def balance_after_formatted(self):
        return "{:.2f}".format(float(self.balance_after))

    def __repr__(self) -> str:
        return f"""{self.transaction_currency_code} \
                {self.amount}{self.user.name}"""

    class InvalidCurrencyException(Exception):
        pass

    class InsufficientBalanceException(Exception):
        pass

    @classmethod
    def interaccount(cls, sender, recipient, amount, description=None):
        """
        Transfer amount from sender to reciepient
        Currencies may be different.
        Conversion will be done by the respective accounts
        """
        if not description:
            description = ("Inter-account transfer from"
                           f" {sender.name} to {recipient.name}")
        currency = sender.default_currency_code
        sender.transact(amount, currency, Transaction.Types.Debit,
                        description)
        recipient.transact(amount, currency, Transaction.Types.Credit,
                           description)
        db.session.commit()
