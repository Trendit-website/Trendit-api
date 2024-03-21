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
from ...models import Role, TempUser, Trendit3User, Address, Profile, OneTimeToken, ReferralHistory, Membership, Wallet, UserSettings, Transaction, TransactionType
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.location_helpers import get_currency_info
from ...utils.helpers.auth_helpers import generate_six_digit_code, send_code_to_email, save_pwd_reset_token, send_2fa_code
from ...utils.helpers.user_helpers import is_user_exist, get_trendit3_user, referral_code_exists



class AdminDashboardController:

    @staticmethod
    def admin_dashboard():

        try:

            # Calculate total received payments
            total_received_payments = db.session.query(func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.PAYMENT).scalar() or 0

            # Calculate total payouts
            total_payouts = db.session.query(func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.WITHDRAWAL).scalar() or 0

            # # Calculate total received payments per month
            # received_payments_per_month = db.session.query(func.strftime('%Y-%m', Transaction.created_at),
            #                                             func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.PAYMENT)\
            #                                 .group_by(func.strftime('%Y-%m', Transaction.created_at)).all()

            # # Calculate total payouts per month
            # payouts_per_month = db.session.query(func.strftime('%Y-%m', Transaction.created_at),
            #                                     func.sum(Transaction.amount)).filter_by(transaction_type=TransactionType.WITHDRAWAL)\
            #                                 .group_by(func.strftime('%Y-%m', Transaction.created_at)).all()

            # # Calculate total payment activities per month
            # payment_activities_per_month = db.session.query(func.strftime('%Y-%m', Transaction.created_at),
            #                                                 func.count(Transaction.id)).group_by(func.strftime('%Y-%m', Transaction.created_at)).all()


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


            # Format data for bar chart
            received_payments_per_month_dict = {date: amount for date, amount in received_payments_per_month}
            payouts_per_month_dict = {date: amount for date, amount in payouts_per_month}
            payment_activities_per_month_dict = {date: count for date, count in payment_activities_per_month}

            extra_data = {
                'total_received_payments': total_received_payments,
                'total_payouts': total_payouts,
                'received_payments_per_month': received_payments_per_month_dict,
                'payouts_per_month': payouts_per_month_dict,
                'payment_activities_per_month': payment_activities_per_month_dict
            }

            return success_response('Admin dashboard data', 200, extra_data)
        
        except Exception as e:
            console_log('Admin Dashboard EXCEPTION', str(e))
            current_app.logger.error(f"An error occurred fetching the Admin Dashboard data: {str(e)}")
            db.session.rollback()
            db.session.close()
            return error_response('An error occurred fetching the Admin Dashboard data', 500)
        
        
    @staticmethod
    def create_admin(user_id: int):
        try:
            user = Trendit3User.query.get(user_id)
            if user is None:
                return error_response('User not found', 404)
            
            #TODO: change name from 'Advertiser' to 'Admin'
            
            role = Role.query.filter_by(name='Advertiser').first()
            if role:
                user.roles.append(role)
            
            db.session.commit()
            return success_response('User is now an Admin', 200)
        
        except Exception as e:
            console_log('Create Admin EXCEPTION', str(e))
            current_app.logger.error(f"An error occurred creating an Admin: {str(e)}")
            db.session.rollback()
            db.session.close()
            return error_response('An error occurred creating an Admin', 500)