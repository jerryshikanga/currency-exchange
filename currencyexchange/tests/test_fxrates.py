import os
import json
from decimal import Decimal

from mock import patch

from currencyexchange import db
from currencyexchange import create_app
from .utils import TestCase


class FxRateTests(TestCase):
    def setUp(self) -> None:
        os.environ['FIXER_SECRET_KEY'] = 'test'
        self.app = create_app()
        ctx = self.app.app_context()
        ctx.push()
        return super().setUp()

    @patch('currencyexchange.database.fxrates.requests.get')
    def test_rates_retrieval(self, mock_requests):
        from .utils import delete_all_rates, MockResponse
        from currencyexchange.database.fxrates import FxRate
        delete_all_rates()
        expected_response = ('{"success": true, "timestamp": 1619062744,'
                             ' "base": "EUR", "date": "2021-04-22", "rates": '
                             '{"AED": 4.422861, "AFN": 93.376639, "ALL": '
                             '123.238632, "AMD": 628.811549, "ANG": 2.161392, '
                             '"AOA": 793.029331, "ARS": 111.926674, "AUD": '
                             '1.552483, "AWG": 2.167663, "AZN": 2.040164, '
                             '"BAM": 1.960927, "BBD": 2.43119}}')
        mock_requests.return_value = MockResponse(expected_response)
        FxRate.refresh_from_api()
        aed = FxRate.query.filter_by(target_currency_code='AED').first()
        expected_rate = Decimal(json.loads(expected_response)['rates']['AED'])
        self.assertAlmostEqual(aed.rate, expected_rate)
        expected_response2 = ('{"success": true, "timestamp": 1619062744, '
                              '"base": "EUR", "date": "2021-04-22", "rates": '
                              '{"AED": 16.422861, "AFN": 93.376639}}')
        mock_requests.return_value = MockResponse(expected_response2)
        FxRate.refresh_from_api()
        db.session.refresh(aed)
        expected_rate = Decimal(json.loads(expected_response2)['rates']['AED'])
        self.assertAlmostEqual(aed.rate, expected_rate)

    def test_rate_conversion(self):
        from .utils import delete_all_rates
        from currencyexchange.database.fxrates import FxRate
        delete_all_rates()
        kes_rate = FxRate(target_currency_code='KES', rate=100)
        ugx_rate = FxRate(target_currency_code='UGX', rate=3000)
        db.session.add_all([kes_rate, ugx_rate])
        db.session.commit()
        kes_to_ugx = FxRate.get_rate('KES', 'UGX')
        self.assertEqual(kes_to_ugx, 30)
