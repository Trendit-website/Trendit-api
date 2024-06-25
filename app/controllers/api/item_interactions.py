import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.item import LikeLog, Share, Comment
from app.utils.helpers.item_helpers import fetch_item
from app.utils.helpers.response_helpers import error_response, success_response


class ItemInteractionsController:
    @staticmethod
    def like_item(item_id_slug):
        error = False
        try:
            user_id = get_jwt_identity()
            item = fetch_item(item_id_slug)
            if item is None:
                return error_response("Item not found", 404)
            
            item_id = item.id
            
            like = LikeLog.query.filter_by(user_id=user_id, item_id=item_id).first()
            if like:
                return success_response(f"You have already liked this {item.item_type}", 200)
            
            new_like = LikeLog(user_id=user_id, item_id=item_id)
            db.session.add(new_like)
            db.session.commit()
        except Exception as e:
            error = True
            status_code = 500
            msg = 'Error liking the item'
            logging.exception(f"An exception occurred during liking of Item {item_id}.\n{str(e)}")
        
        if error:
            return jsonify({
                "status": "failed",
                "status_code": status_code,
                "message": msg,
            }), status_code
        else:
            return success_response(f"{item.item_type} liked successfully", 200)


    @staticmethod
    def share_item(item_id_slug):
        error = False
        try:
            user_id = get_jwt_identity()
            item = fetch_item(item_id_slug)
            item_id = item.id
            
            if item is None:
                return jsonify({
                    "status": "failed",
                    "status_code": 404,
                    "message": "Item not found"
                }), 404
            
            share = Share.query.filter_by(user_id=user_id, item_id=item_id).first()
            if share:
                return jsonify({
                    "status": "failed",
                    "status_code": 400,
                    "message": "You have already shared this item"
                }), 400
            
            new_share = Share(user_id=user_id, item_id=item_id)
            db.session.add(new_share)
            db.session.commit()
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error sharing the item"
            logging.exception(f"An exception occurred during sharing of Item {item_id}.\n{str(e)}")
        
        if error:
            return jsonify({
                "status": "failed",
                "status_code": status_code,
                "message": msg,
            }), status_code
        else:
            return jsonify({
                "status": "success",
                "status_code": 200,
                "message": "Item shared successfully"
            }), 200


    @staticmethod
    def view_item(item_id_slug):
        error = False
        try:
            item = fetch_item(item_id_slug)
            if item is None:
                return jsonify({
                    "status": "failed",
                    "status_code": 404,
                    "message": "Item not found"
                }), 404
            
            item_id = item.id
            
            # Check if views_count is None or not defined
            if item.views_count is None:
                item.views_count = 1
            else:
                item.views_count += 1
            
            db.session.commit()
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error viewing the item"
            logging.exception(f"An exception occurred during viewing of Item {item_id}.\n{str(e)}")
        
        if error:
            return jsonify({
                "status": "failed",
                "status_code": status_code,
                "message": msg,
            }), status_code
        else:
            return jsonify({
                "status": "success",
                "status_code": 200,
                "message": f"{item.item_type} viewed successfully"
            }), 200


    @staticmethod
    def add_comment(item_id_slug):
        error = False
        
        try:
            item = fetch_item(item_id_slug)
            if item is None:
                return jsonify({
                    "status": "failed",
                    "status_code": 404,
                    "message": "Item not found"
                }), 404
            
            item_id = item.id
            user_id = get_jwt_identity()
            data = request.get_json()
            comment = data.get('comment')
            
            if not comment:
                return error_response("Comment not provided", 400)
            
                
            new_comment = Comment(user_id=user_id, item_id=item_id, text=comment)
            db.session.add(new_comment)
            db.session.commit()
            extra_data = {'comment_details': new_comment.to_dict()}
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error adding a comment"
            logging.exception(f"An exception occurred during adding a comment to Item {item_id}.\n{str(e)}")
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response("Comment added successfully", 200, extra_data)

