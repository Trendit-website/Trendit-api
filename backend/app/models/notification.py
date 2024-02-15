from datetime import datetime
from sqlalchemy.orm import backref

from app.extensions import db
from app.utils.helpers.basic_helpers import generate_random_string

from app.decorators.auth import roles_required


user_notification = db.Table(
    'user_notification',
    db.Column('user_id', db.Integer, db.ForeignKey('trendit3_user.id')), # change user.id to trendituser.id
    db.Column('notification_id', db.Integer, db.ForeignKey('notification.id'))
)

# Notification model
class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sourceId = db.Column(db.BigInteger, nullable=False)
    sourceType = db.Column(db.String(50), nullable=False)
    type = db.Column(db.SmallInteger, nullable=False, default=0)
    read = db.Column(db.Boolean, nullable=False, default=False)
    trash = db.Column(db.Boolean, nullable=False, default=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=True, default=None)
    content = db.Column(db.Text, nullable=True, default=None)

    user = db.relationship('User', backref=db.backref('notification', lazy=True))
    # targets = db.relationship('Trendit3User', secondary=user_notification, backref='notifications')
    targets = db.relationship('Trendit3User', secondary='user_notification', backref=db.backref('notifications', lazy='dynamic'))

    def __repr__(self):
        return f'<Notification {self.id}>'
    
    @classmethod
    @roles_required('admin')
    def create_notification(cls):
        # notification = cls()
        pass
        

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'created_at': self.createdAt,
            'updated_at': self.updatedAt,
            'content': self.content
        }