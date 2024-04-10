'''
This module defines the controller methods for admin dashboard in the Trendit³ Flask application.

It includes methods for checking username, checking email, signing up, resending email verification code, and logging in.

@author: Chris
@link: https://github.com/al-chris
@package: Trendit³
'''

import logging
import secrets
from datetime import timedelta
from flask import request, current_app
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import UnsupportedMediaType
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError, DecodeError
from sqlalchemy import func

from ...extensions import db
from ...models import Role, RoleNames, TempUser, Trendit3User, Task, TaskStatus, OneTimeToken, ReferralHistory, Membership, Wallet, UserSettings, Transaction, TransactionType
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.location_helpers import get_currency_info
from ...utils.helpers.auth_helpers import generate_six_digit_code, save_pwd_reset_token, send_2fa_code
from ...utils.helpers.user_helpers import is_user_exist, get_trendit3_user, referral_code_exists
from ...utils.helpers.mail_helpers import send_other_emails
from datetime import datetime, timedelta



def fill_missing_months(data_dict):
    # Define the current date and adjust it to the first day of the month
    current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Calculate the start date as exactly 11 months before the current month
    start_date = current_date - timedelta(days=365.25/12 * 11)

    for _ in range(12):  # Iterate exactly 12 times
        # Format the start_date to "YYYY-MM" format
        formatted_date = start_date.strftime('%Y-%m')
        # If this month isn't in the data dictionary, add it with a 0 value
        data_dict.setdefault(formatted_date, 0)
        # Move to the next month
        # Adjusting month and year as necessary
        if start_date.month == 12:
            start_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            start_date = start_date.replace(month=start_date.month + 1)


class AdminDashboardController:

    @staticmethod
    def admin_dashboard():

        try:

            # Calculate total received payments
            total_received_payments = db.session.query(func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.PAYMENT).scalar() or 0

            # Calculate total payouts
            total_payouts = db.session.query(func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.WITHDRAWAL).scalar() or 0

            # Calculate total received payments per month
            received_payments_per_month = db.session.query(func.to_char(Transaction.created_at, 'YYYY-MM'),
                                                        func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.PAYMENT)\
                                                    .group_by(func.to_char(Transaction.created_at, 'YYYY-MM')).all()

            # Calculate total payouts per month
            payouts_per_month = db.session.query(func.to_char(Transaction.created_at, 'YYYY-MM'),
                                                func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.WITHDRAWAL)\
                                                    .group_by(func.to_char(Transaction.created_at, 'YYYY-MM')).all()

            # Calculate total payment activities per month
            payment_activities_per_month = db.session.query(func.to_char(Transaction.created_at, 'YYYY-MM'),
                                                            func.count(Transaction.id)).group_by(func.to_char(Transaction.created_at, 'YYYY-MM')).all()

            # Calculate total number of users with the role of earner
            total_earner_users = Trendit3User.query.filter(Trendit3User.roles.any(name=RoleNames.EARNER)).count()

            # Calculate total number of users with the role of advertiser
            total_advertiser_users = Trendit3User.query.filter(Trendit3User.roles.any(name=RoleNames.ADVERTISER)).count()
            
            # Calculate total number of approved tasks
            total_approved_tasks = Task.query.filter_by(status=TaskStatus.APPROVED).count()


            # Calculate total number of new users per month
            new_users_per_month = db.session.query(func.to_char(Trendit3User.date_joined, 'YYYY-MM'),
                                                   func.count(Trendit3User.id)).group_by(func.to_char(Trendit3User.date_joined, 'YYYY-MM')).all()


            # Format data for bar chart
            received_payments_per_month_dict = {date: amount for date, amount in received_payments_per_month}
            payouts_per_month_dict = {date: amount for date, amount in payouts_per_month}
            payment_activities_per_month_dict = {date: count for date, count in payment_activities_per_month}
            new_users_per_month_dict = {date: count for date, count in new_users_per_month}

            # Fill missing months with zeros
            fill_missing_months(received_payments_per_month_dict)
            fill_missing_months(payouts_per_month_dict)
            fill_missing_months(payment_activities_per_month_dict)
            fill_missing_months(new_users_per_month_dict)

            extra_data = {
                'total_received_payments': total_received_payments,
                'total_payouts': total_payouts,
                'received_payments_per_month': received_payments_per_month_dict,
                'payouts_per_month': payouts_per_month_dict,
                'payment_activities_per_month': payment_activities_per_month_dict,
                'new_users_per_month': new_users_per_month_dict,
                'total_advertisers': total_advertiser_users,
                'total_earners': total_earner_users,
                'total_approved_tasks': total_approved_tasks
            }

            return success_response('Admin dashboard data', 200, extra_data)
        
        except Exception as e:
            console_log('Admin Dashboard EXCEPTION', str(e))
            current_app.logger.error(f"An error occurred fetching the Admin Dashboard data: {str(e)}")
            db.session.rollback()
            db.session.close()
            return error_response('An error occurred fetching the Admin Dashboard data', 500)
        
        
    @staticmethod
    def create_admin(type: str=RoleNames.JUNIOR_ADMIN):
        try:
            data = request.get_json()
            # user_id = data.get('user_id')
            email = data.get('email')

            # user = Trendit3User.query.get(user_id)
            user = Trendit3User.query.filter_by(email=email).first()

            if user is None:
                return error_response('User not found', 404)
            
            
            role = Role.query.filter_by(name=type).first()
            if role:
                user.roles.append(role)
            
            db.session.commit()
            extra_data = {'user_roles': [role.name.value for role in user.roles]}
            send_other_emails(user.email, email_type='new_admin')
            db.session.close()
            return success_response('User is now an Admin', 200, extra_data)
        
        except Exception as e:
            console_log('Create Admin EXCEPTION', str(e))
            current_app.logger.error(f"An error occurred creating an Admin: {str(e)}")
            db.session.rollback()
            db.session.close()
            return error_response('An error occurred creating an Admin', 500)
        


