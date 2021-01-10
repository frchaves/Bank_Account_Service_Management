import json, datetime
import database
from validation_methods import check_valid_currency, check_valid_iban, convert_amount_currency
import requests
from flask import Flask, request, abort, Blueprint
from models import db, Accounts, Transactions
from flask_restx import Api, Resource, fields

# from setup import create_app


# import config - docker


bp = Blueprint('bp_routes', __name__)
api = Api(bp, version='1.0', title='Account Service Management API',
    description='To manage bank accounts',)


account_ns = api.namespace('Accounts',
                   description='Operations of accounts')

transaction_ns = api.namespace('Transactions',
                   description='Operations of transactions')

account_model = api.model('Account', {
    'name': fields.String,
    'IBAN': fields.String,
    "balance": fields.Float,
    "currency": fields.String,
})

transaction_model = api.model("Transactions", {
    "from_IBAN": fields.String,
    "to_IBAN": fields.String,
    "account_id": fields.Integer,
    "amount": fields.Float,
    "send_currency": fields.String,
    "receive_currency": fields.String
})

@bp.route('/accounts', methods=['GET'])
@account_ns.route('/accounts')
class ReadAllAccounts(Resource):
    def get(self):
        """
        Reads the accounts from the DB
        A HTTP status code (200) if read was OK and the JSON object with
        all accounts from DB
        JSON with the account (id,name,iban,balance,transactions)
        """
        accounts = database.get_all(Accounts)
        all_accounts = []
        for account in accounts:
            all_transactions = []
            for transaction in account.transactions:
                all_transactions.append(transaction.id)
            new_account = {
                "id": account.id,
                "name": account.name,
                "iban": account.iban,
                "balance": float(account.balance),
                "currency": account.currency,
                "transactions ids": all_transactions
            }

            all_accounts.append(new_account)
        return json.dumps(all_accounts), 200


@bp.route('/account/<iban>', methods=['GET'])
@account_ns.route('/account/<iban>')
class ReadOneAccount(Resource):
    def get(self, iban):
        """
        Reads an accounts from the DB
        A HTTP status code (200) if read was OK and the JSON object with
        the account from DB
        :param iban:
        :return: JSON with the account (id,name,iban,balance,transactions)
        """
        account = database.get_one(Accounts, iban=iban)
        all_transactions = []
        for transaction in account.transactions:
            all_transactions.append(transaction.id)
        read_account = {
            "id": account.id,
            "name": account.name,
            "iban": account.iban,
            "balance": float(account.balance),
            "currency": account.currency,
            "transactions": all_transactions
        }
        return json.dumps(read_account), 200


@bp.route('/account/add', methods=['POST'])
@account_ns.route('/account/add')
class CreateAccounts(Resource):
    @api.expect(account_model)
    def post(self):
        """
        Create accounts from a list of accounts
        A HTTP response 200 OK with the added IBANs
        """

        data = request.get_json()

        all_iban = []
        for account in data:
            name = data[account]['name']
            iban = data[account]['IBAN']
            iban_check = iban.replace(" ", "")

            # Uses the Openiban API to recognize IBANs
            openiban_url = f"https://openiban.com/validate/{iban_check}?getBIC=true&validateBankCode=true"
            response = requests.get(url=openiban_url).json()

            if response['valid'] is False:
                abort(406,f"Openiban says account with iban {iban} is not valid")
            balance = data[account]['balance']
            currency = data[account]['currency']
            if currency != 'EUR' and currency != 'USD':
                abort(406, f"currency {currency} is not valid. Please insert either EUR or USD")

            database.add_instance(Accounts, name=name, iban=iban, balance=balance, currency=currency)
            all_iban.append(iban)

        return json.dumps(f"Added accounts with the IBANs: {all_iban}"), 200


@bp.route('/edit/<iban>', methods=['PATCH'])
@account_ns.route('/account/edit/<iban>')
class UpdateAccount(Resource):
    @api.expect(account_model)
    def patch(self, iban):
        account = database.get_one(Accounts, iban=iban)
        data = request.get_json()
        new_name = data['name']
        new_balance = data['balance']
        new_currency = data['currency']
        iban = data['IBAN']
        iban_check = iban.replace(" ", "")
        if new_currency != "EUR" and new_currency != "USD":
            abort(
                406,
                f"currency {new_currency} is not valid. Please insert either EUR or USD",
            )
        # Uses the Openiban API to recognize IBANs
        openiban_url = f"https://openiban.com/validate/{iban_check}?getBIC=true&validateBankCode=true"
        response = requests.get(url=openiban_url).json()

        if response['valid'] is False:
            abort(
                406,
                f"Openiban says account with iban {iban} is not valid",
            )
        database.edit_instance(Accounts, id=account.id, name=new_name, balance=new_balance, iban=iban, currency=new_currency)
        return json.dumps(f"Edited account with IBAN {iban}"), 200


@bp.route('/remove/<iban>', methods=['DELETE'])
@account_ns.route('/account/remove/<iban>')
class DeleteAccount(Resource):
    def delete(self, iban):
        account = database.get_one(Accounts, iban=iban)
        acc_id = account.id
        database.delete_instance(Accounts, id=acc_id)
        return json.dumps(f"Deleted account number {acc_id} with IBAN: {iban}"), 200


################## TRANSACTIONS ##########################

@bp.route('/transactions', methods=['GET'])
@transaction_ns.route('/transactions')
class ReadTransactions(Resource):
    def get(self):
        transactions = database.get_all(Transactions)
        all_transactions = []
        for transaction in transactions:
            new_transaction = {
                "id": transaction.id,
                "from_IBAN": transaction.from_IBAN,
                "to_IBAN": transaction.to_IBAN,
                "amount": float(transaction.amount),
                "send_currency": transaction.send_currency,
                "receive_currency": transaction.receive_currency,
                "timestamp": datetime.datetime.isoformat(transaction.dt_obj)
            }

            all_transactions.append(new_transaction)
        return json.dumps(all_transactions), 200


@bp.route('/transactions/add', methods=['POST'])
@transaction_ns.route('/transactions/add')
class CreateTransactions(Resource):
    @api.expect(transaction_model)
    def post(self):
        data = request.get_json()

        from_IBAN = data['from_IBAN']
        account_id = data['account_id']
        to_IBAN = data['to_IBAN']
        amount = data['amount']
        send_currency = data['send_currency']
        receive_currency = data['receive_currency']


        if check_valid_iban(from_IBAN) and check_valid_iban(to_IBAN) \
            and check_valid_currency(send_currency) and check_valid_currency(receive_currency):

            # Get accounts

            sender_account = json.loads(ReadOneAccount.get(self, from_IBAN)[0])
            receiver_account = json.loads(ReadOneAccount.get(self, to_IBAN)[0])

            # sender_account = json.loads(read_one(from_IBAN)[0])
            # receiver_account = json.loads(read_one(to_IBAN)[0])

            sender_balance = sender_account['balance']
            receiver_balance = receiver_account['balance']

            sender_currency = sender_account['currency']
            receiver_currency = receiver_account['currency']

            converted_amount = convert_amount_currency(amount, sender_currency, receiver_currency)
            converted_balance = convert_amount_currency(sender_balance, sender_currency, receiver_currency)

            if converted_amount <= converted_balance:
                receiver_balance = receiver_balance + converted_amount
                sender_balance = sender_balance - amount
                dt_obj = datetime.datetime.isoformat(datetime.datetime.now())


                # update accounts
                database.edit_instance(Accounts, id=sender_account['id'], name=sender_account['name'], balance=sender_balance,
                                       iban=sender_account['iban'], currency=sender_account['currency'])
                database.edit_instance(Accounts, id=receiver_account['id'], balance=receiver_balance)

                database.add_instance(Transactions, from_IBAN=from_IBAN, to_IBAN=to_IBAN,
                                      amount=amount, send_currency=send_currency, receive_currency=receive_currency,
                                      dt_obj=dt_obj, account_id=sender_account['id'])

                return json.dumps(f"Moved {converted_amount}{receiver_currency} from IBAN: {from_IBAN} "
                                  f"to IBAN: {to_IBAN}."), 200

                        #Check transaction log
            else:
                return abort(406, f"Insufficient (converted) amount: {converted_amount}{send_currency} to send "
                                  f"from balance: {converted_balance}{send_currency}.")



# ADDED MINE
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{"mestrehackao"}:{"psqltest"}@{"localhost"}:{"5432"}/{"flaskdb"}'


def create_app():
    flask_app = Flask(__name__)
    # flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.app_context().push()
    flask_app.register_blueprint(bp)
    db.init_app(flask_app)
    db.create_all()
    return flask_app


app = create_app()


# RUN
if __name__ == '__main__':
    app.run()
