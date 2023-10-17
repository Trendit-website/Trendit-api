import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.item import Item, LikeLog, Share, Comment


class ItemInteractionsController:
    @staticmethod
    def like_item(item_id):
        error = False
        try:
            user_id = get_jwt_identity()
            item = Item.query.get(item_id)
            
            if item is None:
                return jsonify({
                    "status": "failed",
                    "status_code": 404,
                    "message": "Item not found"
                }), 404
            
            like = LikeLog.query.filter_by(user_id=user_id, item_id=item_id).first()
            if like:
                return jsonify({
                    "status": "failed",
                    "status_code": 400,
                    "message": "You have already liked this item"
                }), 400
            
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
            return jsonify({
                "status": "success",
                "status_code": 200,
                "message": "Item liked successfully"
            }), 200


    @staticmethod
    def share_item(item_id):
        error = False
        try:
            user_id = get_jwt_identity()
            item = Item.query.get(item_id)
            
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
    def view_item(item_id):
        error = False
        try:
            item = Item.query.get(item_id)
            
            if item is None:
                return jsonify({
                    "status": "failed",
                    "status_code": 404,
                    "message": "Item not found"
                }), 404
            
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
                "message": "Item viewed successfully"
            }), 200


    @staticmethod
    def add_comment(item_id):
        error = False
        
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            item = Item.query.get(item_id)
            
            if item is None:
                return jsonify({
                    "status": "failed",
                    "status_code": 404,
                    "message": "Item not found"
                }), 404
                
            new_comment = Comment(user_id=user_id, item_id=item_id, text=data['text'])
            db.session.add(new_comment)
            db.session.commit()
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error adding a comment"
            logging.exception(f"An exception occurred during adding a comment to Item {item_id}.\n{str(e)}")
        
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
                "message": "Comment added successfully"
            }), 200

