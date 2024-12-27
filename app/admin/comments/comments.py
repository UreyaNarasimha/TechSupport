from flask import jsonify, request
from flask_restx import Resource
from app.user.models.models import User, Queries, Comments,Opinion
from app import app, db
from app.authentication import encode_auth_token,authentication,is_active
from app.user.serilalizer.serilalizer import comments_serializer
from app.user.pagination.pagination import get_paginated_list
from sqlalchemy import or_, and_, desc, asc

class AdminComment(Resource):
    
    @authentication
    def put(self):
        
        data = request.get_json() or {}
        
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')
        edited_comment = data.get('edited_comment')
        if not (query_id and user_id and edited_comment and comment_id):
            app.logger.info("query_id , user_id , edited_comment and comment_id are required fields")
            return jsonify(status=400, message="query_id , user_id , edited_comment and comment_id are required fields")
        
        check_user = db.session.query(User).filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=404,message="user not found")
        
        active=is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404,message="admin disabled temporarily")
        
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to update comments")
            return jsonify(status=404, data={}, message="User not allowed to update comments")
        
        check_query=db.session.query(Queries).filter_by(id=query_id,status=True).first()
        if not check_query:
            app.logger.info("query not found")
            return jsonify(status=404,message="query not found")
        
        check_comment=db.session.query(Comments).filter_by(id=comment_id,status=True).first()
        if not check_comment:
            app.logger.info("comment not found")
            return jsonify(status=404,message="comment not found")
        
        check_comment.msg = edited_comment
        db.session.commit()
        app.logger.info("Comment edited")
        return jsonify(status=200, message="Comment edited",
                       data={"query_id": query_id, "comment_id": comment_id, "edited_comment": edited_comment})

    @authentication
    def delete(self):
     
        query_id = request.args.get('query_id')
        user_id = request.args.get('user_id')
        comment_id = request.args.get('comment_id')

        if not (query_id and user_id and comment_id):
            app.logger.info("Query_id , user_id and comment_id are required")
            return jsonify(status=200, message="Query_id , user_id and comment_id are required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("User not allowed to delete comments")
            return jsonify(status=404, data={}, message="User not allowed to delete comments")

        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        if not query_check:
            app.logger.info("Query not found")
            return jsonify(status=400, message="Query not found")

        comment_check = db.session.query(Comments).filter_by(id=comment_id).first()
        if not comment_check:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")
        
        delete_likes_dislikes_comment = Opinion.query.filter_by(c_id=comment_id).all()
        for itr in delete_likes_dislikes_comment:
            db.session.delete(itr)
            db.session.commit()
        comment_check.status = False
        db.session.commit()
        app.logger.info("Comment deleted successfully")
        return jsonify(status=200, message="Comment deleted successfully")

    @authentication
    def get(self):  # send all the comments
        
        query_type = request.args.get('query', None) # #getting key for search
        value = request.args.get('value', None) 
        user_id = request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=404, message="user_id required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")
        
        comment_objs = db.session.query(Comments).order_by(Comments.updated_at)
        if not comment_objs:
            app.logger.info("No record found")
            return jsonify(status=404, message="No record found")
        
        if query_type == 'search':
            comment_objs = comment_objs.filter(Comments.msg.ilike(f"%{value}%"))

        c_list = []
        for itr in comment_objs:
            dt = comments_serializer(itr)
            c_list.append(dt)

        page = f'/admin/comments?user_id={user_id}'

        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning comments data")
    
class AdminGetCommentsByCommentId(Resource):
    
    @authentication
    def get(self): #send comment based on comment_id
        
        comment_id= request.args.get('comment_id')
        if not comment_id:
            app.logger.info("comment_id required")
            return jsonify(status=404, message="comment_id required")
        
        comment_obj = db.session.query(Comments).filter_by(id=comment_id).first()
        if not comment_obj:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")

        data = comments_serializer(comment_obj)
        app.logger.info("Returning comment data")
        return jsonify(status=200, data = data, message="Returning comment data")

class AdminGetCommentsByUserId(Resource):
    
    @authentication
    def get(self): #send all the comments based on user_id
        
        query_type = request.args.get('query', None) # #getting key for search
        value = request.args.get('value', None)  
        user_id= request.args.get('user_id')
        requested_user_id = request.args.get('requested_user_id')
        if not (user_id and requested_user_id):
            app.logger.info("user_id and requested_user_id are required")
            return jsonify(status=404, message="user_id and requested_user_id are required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")
        
        requested_user_check = db.session.query(User).filter_by(id=requested_user_id).first()
        if not requested_user_check:
            app.logger.info("Requested user not found")
            return jsonify(status=400, message="Requested user not found")
        
        comment_objs = db.session.query(Comments).filter_by(u_id=requested_user_id)
        if not comment_objs:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")
        
        if query_type == 'search':
            comment_objs = comment_objs.filter(Comments.msg.ilike(f"%{value}%"))

        c_list = []
        for itr in comment_objs:
            dt = comments_serializer(itr)
            c_list.append(dt)

        if not c_list:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")

        page = f"/admin/commentsbyuserid?user_id={user_id}&requested_user_id={requested_user_id}"
        app.logger.info("Returning comments data")
        return jsonify(status=200, data = get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                  limit=request.args.get('limit', 3),with_params=True),
                                  message="Returning comments data")
