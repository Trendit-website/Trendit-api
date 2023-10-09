from app.extensions import db


# Define the User data model. Make sure to add flask_login UserMixin!!
class Membership(db.Model):
    __tablename__ = "membership"
    
    id = db.Column(db.Integer(), primary_key=True)
    activation_fee_paid = db.Column(db.Boolean, default=False)
    item_upload_paid = db.Column(db.Boolean, default=False)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), unique=True, nullable=False)
    trendit3_user = db.relationship('Trendit3User', back_populates="membership")
    
    def __repr__(self):
        return f'<Membership ID: {self.id}, User ID: {self.user_id}, activation paid: {self.activation_fee_paid}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'activation_fee_paid': self.activation_fee_paid,
            'item_upload_paid': self.item_upload_paid,
            'trendit3_user_id': self.trendit3_user_id,
        }
