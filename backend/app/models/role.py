'''
from app.extensions import db

# Define the User Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    # Define the many-to-many relationship with Permission
    permissions = db.relationship('Permission', secondary='role_permission', back_populates='roles')

class Permission(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # Define the many-to-many relationship with Role
    roles = db.relationship('Role', secondary='role_permission', back_populates='permissions')
    

# Intermediate table for Role-Permission relationship
role_permission = db.Table('role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)
'''