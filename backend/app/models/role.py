from app.extensions import db


# Association table for the many-to-many relationship
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('trendit3_user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# Role data model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=True)


def create_roles():
    roles = ['Admin', 'Moderator', 'Advertiser', 'Earner']

    for role in roles:
        if not Role.query.filter_by(name=role).first():
            new_role = Role(name=role)
            db.session.add(new_role)

    db.session.commit()
