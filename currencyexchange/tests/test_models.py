import os
import json
from unittest import TestCase

from requests import Response
from mock import patch

from currencyexchange import db
from currencyexchange.database.fxrates import FxRate
from currencyexchange import create_app


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email and hashed_password fields are defined correctly
    """
    pass


def delete_all_rates():
    db.session.query(FxRate).delete()
    db.session.commit()


class FxRateTests(TestCase):
    def setUp(self) -> None:
        os.environ['FIXER_SECRET_KEY'] = 'test'
        self.app = create_app()
        ctx = self.app.app_context()
        ctx.push()
        return super().setUp()

    @patch('currencyexchange.database.fxrates.requests')
    def test_rates_retrieval(self, mock_requests):
        delete_all_rates()
        response = Response()
        response.status_code = 200
        expected_response = {
            "success": True,
            "timestamp": 1619062744,
            "base": "EUR",
            "date": "2021-04-22",
            "rates": {
                "AED": 4.422861,
                "AFN": 93.376639,
                "ALL": 123.238632,
                "AMD": 628.811549,
                "ANG": 2.161392,
                "AOA": 793.029331,
                "ARS": 111.926674,
                "AUD": 1.552483,
                "AWG": 2.167663,
                "AZN": 2.040164,
                "BAM": 1.960927,
                "BBD": 2.43119
            }
        }
        response.raw = json.dumps(expected_response)
        mock_requests.return_value = response

        FxRate.refresh_from_api()
        # aed = FxRate.query.filter_by(target_currency_code='AED').first()
        # self.assertAlmostEqual(aed.rate, expected_response['rates']['AED'])

    def test_rate_conversion(self):
        delete_all_rates()
        kes_rate = FxRate(target_currency_code='KES', rate=100)
        ugx_rate = FxRate(target_currency_code='UGX', rate=3000)
        db.session.add_all([kes_rate, ugx_rate])
        db.session.commit()
        kes_to_ugx = FxRate.get_rate('KES', 'UGX')
        self.assertEqual(kes_to_ugx, 30)
