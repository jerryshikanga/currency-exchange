from unittest import TestCase

import pytest
from werkzeug.security import generate_password_hash

from currencyexchange import create_app
from currencyexchange.database.auth import User


@pytest.fixture(scope='module')
def new_user():
    user = User(email='test@domain.com', name='John Doe',
                password=generate_password_hash('password', method='sha256'))
    return user


class AuthViewTest(TestCase):
    def test_home_page(self):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
        """
        flask_app = create_app()

        # Create a test client using the Flask
        # application configured for testing
        with flask_app.test_client() as test_client:
            response = test_client.get('/')
            assert response.status_code == 200
            expected_messages = [
                b"Currency Exchange",
                b"Send and Receive Money in All Major Currencies!"
            ]
            for m in expected_messages:
                assert m in response.data
