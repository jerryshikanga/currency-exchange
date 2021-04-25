# flake8: noqa
from flask import Blueprint, jsonify

from currencyexchange.database.fxrates import FxRate

fxrates = Blueprint('fxrates', __name__)

@fxrates.route('/refresh_fx_rates')
def refresh_fx_rates():
    count = FxRate.refresh_from_api()
    if count:
        response = dict(status="SUCCESS", count=count)
    else:
        response = dict(status="FAILED", count=None)
    return jsonify(response)
