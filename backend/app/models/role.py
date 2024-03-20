from enum import Enum
from slugify import slugify
from sqlalchemy import inspect

from ..extensions import db

class RoleNames(Enum):
    """ENUMS for the name filed in Role Model"""
    SUPER_ADMIN = 'Super Admin'
    Admin = 'Admin'
    JUNIOR_ADMIN = 'Junior Admin'
    ADVERTISER = 'Advertiser'
    EARNER = 'Earner'
    CUSTOMER = 'Customer'

# Association table for the many-to-many relationship
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('trendit3_user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# Role data model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(RoleNames), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=True)



def create_roles(clear=False):
    """Creates default roles if the 'role' table doesn't exist.

    Args:
        clear (bool, optional): If True, clears all existing roles before creating new ones. Defaults to False.
    """
    if not inspect(db.engine).has_table('role'):
        if clear:
            # Clear existing roles before creating new ones
            Role.query.delete()
            db.session.commit()
        
        for role_name in RoleNames:
            if not Role.query.filter_by(name=role_name).first():
                new_role = Role(name=role_name, slug=slugify(str(role_name)))
                db.session.add(new_role)
        db.session.commit()
    