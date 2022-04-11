from flask import session, redirect, url_for, render_template, request, flash
from functools import wraps
from pay_app import app
from pay_app.models import User
from pay_app.wallet.wallet import Wallet

users = User()
wallets = Wallet()


# create login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' in session and session['user_id'] is not None:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

# decorator for checking if user is logged in
# if already logged in, redirect to dashboard


def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' in session and session['user_id'] is not None:
            return redirect(url_for('dashboard'))
        else:
            return f(*args, **kwargs)
    return wrap


@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['POST', 'GET'])
@not_logged_in
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.authenticate(username, password)
        if not user:
            err_msg = 'User not found or password incorrect'
            return render_template('login.html', err_msg=err_msg)

        session['username'] = username
        session['user_id'] = users.get_user_by_username(username)['id']
        return redirect('/dashboard')
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
@not_logged_in
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if users.get_user_by_username(username):
            err_msg = 'Username already exists'
            return render_template('signup.html', err_msg=err_msg)

        users.add_user(username, password)
        return redirect('/login')
    else:
        return render_template('signup.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/make/payment', methods=['POST', 'GET'])
@login_required
def make_payment():
    if request.method == 'GET':
        return render_template('make_payment.html')


@app.route('/wallet/new', methods=['GET'])
@login_required
def new_wallet():
    user = users.get_user_by_username(session['username'])
    user_wallet = wallets.generate_address()
    # add wallet to user dict
    # user.update({'wallet': user_wallet})
    return render_template('wallet.html', user_wallet=user_wallet)


@app.route('/wallet')
@login_required
def wallet():
    return render_template('wallet.html')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port, debug=True)
