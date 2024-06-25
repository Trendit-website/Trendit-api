from app.extensions import db


# Define the User data model. Make sure to add flask_login UserMixin!!
class Membership(db.Model):
    __tablename__ = "membership"
    
    id = db.Column(db.Integer(), primary_key=True)
    membership_fee_paid = db.Column(db.Boolean, default=False)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), unique=True, nullable=False)
    trendit3_user = db.relationship('Trendit3User', back_populates="membership")
    
    def __repr__(self):
        return f'<Membership ID: {self.id}, User ID: {self.user_id}, Membership paid: {self.membership_fee_paid}>'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self, user=False):
        user_info = {'user': self.trendit3_user.to_dict(),} if user else {'user_id': self.trendit3_user_id} # optionally include user info in dict
        return {
            'id': self.id,
            'membership_fee_paid': self.membership_fee_paid,
            **user_info,
        }
