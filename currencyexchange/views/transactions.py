from flask import Blueprint, render_template
from flask_login import login_required

transactions = Blueprint('transactions',  __name__)

@transactions.route('/send_to_internal_account')
@login_required
def send_to_internal_account():
    return render_template('send_to_internal_account.html')


@transactions.route('/send_to_internal_account_post', methods=['POST'])
@login_required
def send_to_internal_account_post():
    return "success"
