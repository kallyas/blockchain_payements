from datetime import datetime
from flask import session, redirect, url_for, render_template, request, flash, jsonify
from functools import wraps
from pay_app import app
from pay_app.models import User
from pay_app.block.block import Block
from pay_app.transactions.transactions import Transaction
from pay_app.wallet.wallet import Wallet
from pay_app.blockchain.blockchain import Blockchain

users = User()
wallets = Wallet()
blockchain = Blockchain()

SENDER_ADDR = "CIT COIN"
MINING_REWARD = 10


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

@app.route('/send-money', methods=['GET'])
@login_required
def send_money():
    return render_template('send-money.html')


@app.route('/wallet/new', methods=['POST'])
@login_required
def new_wallet():
    user = users.get_user_by_username(session['username'])
    user_wallet = wallets.generate_address()
    # add wallet to user dict
    # user.update({'wallet': user_wallet})
    return {'address': user_wallet}

@app.route('/wallet')
@login_required
def wallet():
    return render_template('wallet.html')

@app.route("/transactions/get")
@login_required
def get_transactions():
    return { 'transactions': blockchain.transactions }

@app.route("/mine")
@login_required
def mine():
    data = blockchain.mine(SENDER_ADDR, blockchain.node_id, MINING_REWARD)
    return { 'block': data }

@app.route("/chain")
@login_required
def get_chain():
    chain_dict = [chain.to_dict() for chain in blockchain.chain]
    return {'chain': chain_dict, 'length': len(chain_dict)}

@app.route("/nodes/register")
@login_required
def register_nodes():
    nodes = request.get_json()
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/generate/transaction', methods=['POST'])
@login_required
def generate_transaction():
    data = request.get_json()
    required_data = ['sender_address', 'recipient_address', 'amount', 'sender_private_key']
    if not all(k in data for k in required_data):
        return {'message': 'Missing values'}, 400

    sender_address = data['sender_address']
    sender_private_key = data['sender_private_key']
    recipient_address = data['recipient_address']
    amount = data['amount']
    transaction = Transaction(sender_address, sender_private_key, recipient_address, amount)
    response = {'transaction': transaction.to_dict(), 'signature': transaction.sign_transaction()}
    return jsonify(response), 201

@app.route('/transactions/new', methods=['POST'])
@login_required
def new_transaction():
    data = request.get_json()
    transaction_keys = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(key in data for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    block_data = {
        'sender_address': data['sender_address'],
        'recipient_address': data['recipient_address'],
        'amount': data['amount'],
        'signature': data['signature'],
        'nonce': blockchain.proof_of_work(blockchain.last_block)
    }
    block = Block(len(blockchain.chain), block_data, datetime.now(), blockchain.last_block.hash)
    blockchain_response = blockchain.add_block(block)
    if blockchain_response:
        response = {'message': 'Block added to the chain', 'block': block.to_dict(), 'chain': blockchain.chain}
        return jsonify(response), 201
    else:
        response = {'message': 'Block not added to the chain', 'chain': blockchain.chain}
        return jsonify(response), 409


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port, debug=True)
