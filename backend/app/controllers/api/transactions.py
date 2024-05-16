import os
import io
import logging
import pandas as pd
import requests
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, SQLAlchemyError )
from flask import request, send_file, jsonify, url_for
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from PIL import Image as PILImage
from io import BytesIO

from ...models import Trendit3User, Payment, Transaction, TransactionType
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.payment_helpers import get_total_amount_earned, get_total_amount_spent


class TransactionController:
    @staticmethod
    def get_transaction_history():
        """
        Fetches the transaction history for a user.

        This function extracts the current_user_id from the jwt identity, checks if the user exists, and if so, fetches the user's payment transaction from the database and returns it. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the request, a status code, a message (and payment history in case of success), and an HTTP status code.
        """
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            per_page = 15
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            # Fetch transaction records from the database
            pagination = Transaction.query.filter_by(trendit3_user_id=current_user_id) \
                .order_by(Transaction.created_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            
            transactions = pagination.items
            current_transactions = [transaction.to_dict() for transaction in transactions]
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "transactions_history": current_transactions,
            }
            
            if not transactions:
                return success_response(f'No transactions has been made', 200, extra_data)
            
            api_response = success_response('Transaction history fetched successfully', 200, extra_data)
        except Exception as e:
            log_exception(f"An exception occurred fetching transaction history", e)
            api_response = error_response("An error occurred while processing the request", 500)
        
        return api_response

    
    @staticmethod
    def get_funding_history():
        """
        Fetches the Payment history that have payment type as "credit-wallet" for a user.

        This function extracts the current_user_id from the jwt identity, checks if the user exists, and if so, fetches the user's Payment history from the database and returns it. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the request, a status code, a message (and payment history in case of success), and an HTTP status code.
        """
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            per_page = 15
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            # Fetch transaction records from the database
            pagination = Payment.query.filter_by(trendit3_user_id=current_user_id, payment_type='credit-wallet') \
                .order_by(Payment.created_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            wallet_credits = pagination.items
            current_wallet_credit = [wallet_credit.to_dict() for wallet_credit in wallet_credits]
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "funding_history": current_wallet_credit,
            }
            
            if not wallet_credits:
                return success_response(f'You have no history funding your wallet', 200, extra_data)
            
            api_response = success_response('Funding history fetched successfully', 200, extra_data)
        except Exception as e:
            log_exception(f"An exception occurred fetching Funding history", e)
            api_response = error_response("An unexpected error occurred", 500)
        
        return api_response

    
    @staticmethod
    def get_transaction_stats():
        try:
            # get the current user's ID
            current_user_id = get_jwt_identity()
            
            # Check if user exists
            current_user = Trendit3User.query.get(current_user_id)
            if current_user is None:
                return error_response('User not found', 404)
            
            # get the user's wallet balance
            wallet_balance = current_user.wallet_balance
            
            
            # get the total earnings for the current month and overall
            total_earned_overall, total_earned_current_month = get_total_amount_earned(current_user_id)
            
            # get the total amount spent for the current month and overall
            total_spent_overall, total_spent_current_month = get_total_amount_spent(current_user_id)
            
            
            # create a dictionary with the stats
            metrics = {
                'wallet_balance': wallet_balance,
                'total_earned_overall': total_earned_overall,
                'total_earned_current_month': total_earned_current_month,
                'total_spent_overall': total_spent_overall,
                'total_spent_current_month': total_spent_current_month,
                'currency_code': current_user.wallet.currency_code,
                'currency_name': current_user.wallet.currency_name
            }
            
            api_response = success_response(f"metrics fetched successfully", 200, {"metrics": metrics})
        except Exception as e:
            log_exception(f"An exception occurred fetching transaction metrics.", e)
            api_response = error_response(f"Error fetching transaction metrics: {str(e)}", 500)
        
        return api_response
    

    @staticmethod
    def fetch_transactions(start_date=None, end_date=None):
        # Check if user exists
        user_id = int(get_jwt_identity())
        user = Trendit3User.query.get(user_id)
        if user is None:
            return None, 'User not found', 404

        # Fetch transaction records from the database
        query = Transaction.query.filter_by(trendit3_user_id=user_id)
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)

        transactions = query.order_by(Transaction.created_at.desc()).all()
        current_transactions = [transaction.to_dict() for transaction in transactions]

        if not transactions:
            return None, 'No transactions found for the specified date range', 200

        return current_transactions, 'Transaction history fetched successfully', 200

    @staticmethod
    def generate_pdf(transactions, logo_path):
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []

        # Add logo if path is provided
        if logo_path:
            logo = Image(logo_path)
            logo.drawHeight = 1 * inch  # Example size, adjust as necessary
            logo.drawWidth = 2 * inch
            elements.append(logo)

        # Add a space and title after the logo
        elements.append(Spacer(1, 0.25 * inch))
        title_table = Table([['Transaction History']], colWidths=[doc.width])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
        ]))
        elements.append(title_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Table Header and Data
        table_header = [['ID', 'Key', 'Amount', 'Type', 'Description']]
        table_data = table_header + [[
            str(transaction['id']),
            transaction['key'],
            f"${transaction['amount']:,.2f}",
            transaction['transaction_type'],
            transaction['description']
        ] for transaction in transactions]

        # Create Transaction Table
        transaction_table = Table(table_data, colWidths=[50, 150, 100, 100, 100])
        transaction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        elements.append(transaction_table)

        # Build the document
        doc.build(elements)

        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="transaction_history.pdf", mimetype="application/pdf")


    @staticmethod
    def generate_excel(transactions):
        df = pd.DataFrame(transactions)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Transaction History')

        excel_buffer.seek(0)

        return send_file(excel_buffer, as_attachment=True, download_name="transaction_history.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @staticmethod
    def download_transaction_history():
        try:
            data = request.get_json()
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            file_format = data.get("format", None)  # "pdf" or "excel"

            # Validate date inputs
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            transactions, message, status_code = TransactionController.fetch_transactions(start_date, end_date)
            if transactions is None:
                return jsonify({'message': message}), status_code

            # Generate PDF or Excel file if requested

            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            # Construct the path to the image
            logo_path = os.path.join(BASE_DIR, 'static', 'img', 'Trendit', 'Trendit3-Icon.png')

            if file_format == "pdf":
                return TransactionController.generate_pdf(transactions, logo_path)
            elif file_format == "excel":
                return TransactionController.generate_excel(transactions)
            else:
                return jsonify({'message': "Invalid format specified"}), 400

        except ValueError as ve:
            logging.error(f"ValueError occurred: {ve}")
            return error_response('Invalid data provided', 400)
        except SQLAlchemyError as sae:
            logging.error(f"Database error occurred: {sae}")
            # db.session.rollback()
            return error_response('Database error occurred', 500)

        except Exception as e:
            log_exception(f"An exception occurred while downloading transaction history", e)
            return jsonify({'message': "An error occurred while processing the request"}), 500