import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

transactions = Blueprint('transactions',  __name__)
logger = logging.getLogger(__name__)


@transactions.route('/send_to_internal_account')
@login_required
def send_to_internal_account():
    return render_template('send_to_internal_account.html')


@transactions.route('/send_to_internal_account_post', methods=['POST'])
@login_required
def send_to_internal_account_post():
    amount = request.form.get('amount')
    description = request.form.get('description')
    recipient_email = request.form.get('recipient_email')
    from currencyexchange.database.auth import User
    recipient = User.query.filter_by(email=recipient_email).first()
    if not recipient:
        flash('The recipient cannot be found in our records.')
        return redirect(url_for('transactions.send_to_internal_account'))
    from currencyexchange.database.transactions import Transaction
    kwargs = dict(sender=current_user, recipient=recipient,
                  amount=amount, description=description)
    try:
        Transaction.interaccount(**kwargs)
        return redirect(url_for('main.profile'))
    except Exception:
        logger.error(f"Failed to do inter account transaction {kwargs}")
        return redirect(url_for('transactions.send_to_internal_account'))


@transactions.route('/deposit_mm')
@login_required
def deposit():
    return render_template('deposit.html')


@transactions.route('/deposit_post', methods=['POST'])
@login_required
def deposit_post():
    amount = request.form.get('amount')
    flash(f'Your deposit of {amount} has been received successfully.')
    return redirect(url_for('main.profile'))


@transactions.route('/withdraw_mm')
@login_required
def withdraw():
    return render_template('withdraw.html')


@transactions.route('/withdraw_post', methods=['POST'])
@login_required
def withdraw_post():
    amount = request.form.get('amount')
    flash(f'Your withdrawal of {amount} has been received successfully.')
    return redirect(url_for('main.profile'))
