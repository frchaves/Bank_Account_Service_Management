import flask_sqlalchemy
db = flask_sqlalchemy.SQLAlchemy()


class Accounts(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    iban = db.Column(db.String(34), unique=True, nullable=False)
    balance = db.Column(db.Numeric(20, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    transactions = db.relationship('Transactions', backref='accounts', lazy=True)


class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    from_IBAN = db.Column(db.String(34), unique=True, nullable=False)
    to_IBAN = db.Column(db.String(34), unique=True, nullable=False)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    send_currency = db.Column(db.String(3), nullable=False)
    receive_currency = db.Column(db.String(3), nullable=False)
    dt_obj = db.Column(db.DateTime(), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
