import os
import logging
from datetime import datetime

import requests

from currencyexchange import db

logger = logging.getLogger(__name__)


class FxRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_currency_code = db.Column(db.String(3), default='USD', index=True)
    target_currency_code = db.Column(db.String(3), unique=True, index=True)
    rate = db.Column(db.Float(precision=4, asdecimal=True))
    last_updated = db.Column(db.DateTime(), onupdate=datetime.now)

    def __repr__(self) -> str:
        return f"{self.base_currency_code} To {self.target_currency_code}"

    @classmethod
    def get_rate(cls, from_currency_code: str, target_currency_code: str):
        """
        We want to convert form one currency to another but dont have
        the direct values. So we do a conversion to usd first then
        to next currency. This avoids making extra calls to api
        """
        # cache_key = f"{from_currency_code}_{target_currency_code}_{date}"
        # if cache contains the value we return the ValueError

        if target_currency_code == from_currency_code:
            return 1
        target_rate = FxRate.query.filter_by(
            target_currency_code=target_currency_code).\
            first().rate
        if from_currency_code.upper() == "USD":
            return target_rate
        from_rate = FxRate.query.filter_by(
            target_currency_code=from_currency_code).\
            first().rate
        return target_rate/from_rate

    @classmethod
    def refresh_from_api(cls, base_currency_code='USD'):
        """
        This will run to retrive data from the api and load into the db
        """
        key = os.environ['FIXER_SECRET_KEY']
        url = "http://data.fixer.io/api/latest"
        payload = dict(access_key=key, format=1, base=base_currency_code)
        try:
            api_rates = requests.get(url, params=payload).json()['rates']
            objs_to_add = []
            for key, value in api_rates.items():
                rate_updatable = FxRate.query.filter_by(
                    target_currency_code=key,
                    base_currency_code=base_currency_code
                ).first()
                if rate_updatable:
                    rate_updatable.rate = value
                else:
                    objs_to_add.append(FxRate(target_currency_code=key,
                                              rate=value))
            # use bulk inserts
            db.session.add_all(objs_to_add)
            db.session.commit()
            return len(api_rates)
        except Exception as e:
            logger.error(f"Error retrieving fx rates {e}")
            return None
