# flake8: noqa
from flask import Blueprint

from currencyexchange.database.fxrates import FxRate

fxrates = Blueprint('fxrates', __name__)
