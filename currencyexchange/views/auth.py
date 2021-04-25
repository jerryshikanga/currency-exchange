from currencyexchange.database.transactions import Transaction
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from currencyexchange.database.auth import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it,
    # and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for('auth.login'))

    # if the above check passes,
    # then we know the user has the right credentials
    login_user(user, remember=remember)  # save user in session
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    currency = request.form.get('currency')
    password = request.form.get('password')

    try:
        User.create(email, name, password, currency=currency)
        return redirect(url_for('auth.login'))
    except User.UserExistsException:
        # if a user is found,
        # we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    except Transaction.InvalidCurrencyException:
        flash('The currency is not supported!')
        return redirect(url_for('auth.signup'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/editprofile')
@login_required
def edit_profile():
    return render_template('profile_update_form.html',
                           current_user=current_user)


@auth.route('/editprofilepost', methods=['POST', 'PUT', 'PATCH'])
@login_required
def edit_profile_post():
    email = request.form.get('email')
    name = request.form.get('name')
    currency = request.form.get('currency')

    # convert to our model obj
    user = User.query.filter_by(email=current_user.email).first()

    try:
        user.update(email, name, currency)
        return redirect(url_for('main.profile'))
    except User.UserExistsException:
        flash('Email address already exists')
        return redirect(url_for('auth.edit_profile'))
    except Transaction.InvalidCurrencyException:
        flash('The currency is not supported!')
        return redirect(url_for('auth.edit_profile'))
