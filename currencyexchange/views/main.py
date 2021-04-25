from currencyexchange.database.transactions import Transaction
from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    transactions = Transaction.query.filter_by(user_id=current_user.id)
    kwargs = dict(current_user=current_user, transactions=transactions)
    return render_template('profile_details.html', **kwargs)
