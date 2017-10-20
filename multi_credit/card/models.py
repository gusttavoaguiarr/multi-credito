from multi_credit import db


class Card(db.Model):

    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    expiration_date = db.Column(db.Date)
    validity_date = db.Column(db.Date)
    name = db.Column(db.String(30), nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    limit = db.Column(db.Float(), nullable=False)
    credit = db.Column(db.Float(), nullable=False)

    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    wallet = db.relationship("Wallet")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'number': self.number,
            'expiration_date': self.expiration_date,
            'validity_date': self.validity_date,
            'name': self.name,
            'cvv': self.cvv,
            'limit': self.limit,
            'credit': self.credit,
            'wallet_id': self.wallet_id
        }