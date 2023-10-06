from app.extensions import db
from app.models.user import Trendit3User, Address


def get_user_info(userId):
    '''Gets profile details of a particular user'''
    
    if userId is None:
        userInfo = {}
    else:
        trendit3_user = Trendit3User.query.filter(Trendit3User.id == userId).first()
        address = Address.query.filter(Address.trendit3_user_id == userId).first()
        
        userInfo = {
            'username': trendit3_user.username,
            'email': trendit3_user.email,
            'gender': trendit3_user.gender,
            'date_joined': trendit3_user.date_joined,
            'country': address.country,
            'state': address.state,
            'local_government': address.local_government,
        }
    
    for key in userInfo:
        if userInfo[key] is None:
            userInfo[key] = ''
    
    return userInfo

def validateEmail(email, existingEmail):
    if email != existingEmail:
        user = Trendit3User.query.filter(Trendit3User.email == email).first()
        if user:
            return 'Email already registered'
        else:
            return 'Email not registered'
    else:
        return 'Email not registered'

def validateUsername(username, existingUsername):
    if username != existingUsername:
        user = Trendit3User.query.filter(Trendit3User.username == username).first()
        if user:
            return 'Username already registered'
        else:
            return 'Username not registered'
    else:
        return 'Username not registered'

