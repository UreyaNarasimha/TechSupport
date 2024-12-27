from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restx import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments,Opinion
from app import app, db
from sqlalchemy import or_, and_, desc
from app.authentication import encode_auth_token, authentication,get_user_id,is_active
from app.user.serilalizer.serilalizer import comments_serializer,replace_with_ids
from app.user.pagination.pagination import get_paginated_list
from app.user.fileupload.file_upload import upload_file
from app.utils.form_validations import description_validator

class UserComment(Resource):
    
    @authentication
    def post(self):
                
        data = request.get_json()
        
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        comment = data.get('comment')
        if not (query_id and user_id and comment):
            app.logger.info("query_id,user_id and comment are required")
            return jsonify(status=400, data={}, message="query_id,user_id and comment are required")
        
        file = request.files.get('file')

        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=404, data={}, message="user not found")

        active=is_active(user_id)
        if not active:
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, data={}, message="User is temporarily disabled")
        
        queries_check = Queries.query.filter_by(id=query_id).first()
        if not queries_check:
            app.logger.info("query not found")
            return jsonify(status=404, data={}, message="query not found")
        
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        if file:
            file = upload_file(self, file)
            file_name=file[0]
            file_path=file[1]
        else:
            file_path = None
            file_name = None
        
        comm = Comments(user_id, query_id,comment,file_name,file_path,date_time_obj,date_time_obj)
        db.session.add(comm)
        db.session.commit()
        app.logger.info("comment inserterd succesfully")
        return jsonify(status=200, data={}, message="comment inserterd succesfully")

    @authentication
    def put(self):
        
        data = request.get_json() or {}
    
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')
        edited_comment = data.get('edited_comment')
        if not (user_id and comment_id and edited_comment):
          app.logger.info("user_id,comment_id and edited_comment are required")
          return jsonify(status=400, data={}, message="user_id,comment_id and edited_comment are required")
        
        new_file = request.files.get('file')

        check_user = db.session.query(User).filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=404, data={}, message="user not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data={}, message="user disabled temporarily")

        check_queries_auth = db.session.query(Comments).filter_by(u_id=user_id).first()     
        if not (check_queries_auth):
            app.logger.info("cant edit comment")
            return jsonify(status=404, data={}, message="cant edit comment")
        
        edit_comment_by_id = db.session.query(Comments).filter_by(id=comment_id).first()
        if not edit_comment_by_id:
            app.logger.info("Comment not found")
            return jsonify(status=400, data={}, message="Comment not found")
        
        if not (edit_comment_by_id.u_id == user_id):
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, data={}, message="User not allowed to edit")

        description_check = description_validator(edited_comment)
        if not description_check:
                app.logger.info("Invalid comment")
                return jsonify(status=200, data={}, message="Invalid comment")
        edit_comment_by_id.msg = edited_comment
        if new_file:
            file_data = upload_file(self,new_file)
            new_file_name = file_data[0]
            new_file_path = file_data[1]
        else:
            new_file_name=None
            new_file_path = None
        edit_comment_by_id.filename=new_file_name
        edit_comment_by_id.filepath=new_file_path
        db.session.commit()
        app.logger.info("Comment edited")
        return jsonify(status=200, message="Comment edited",
                        data={"comment_id": comment_id, "edited_comment": edited_comment})

    # @authentication
    def delete(self):
        
        user_id = request.args.get('user_id')
        query_id = request.args.get('query_id')
        comment_id = request.args.get('comment_id')
        if not (user_id and comment_id):
            app.logger.info("user_id, query_id and comment_id are required")
            return jsonify(status=200, data={}, message="user_id, query_id and comment_id are required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data={}, message="user disabled temporarily")
        
        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        if not query_check:
            app.logger.info("Query not found")
            return jsonify(status=400, data={}, message="Query not found")
        
        comment_check = db.session.query(Comments).filter_by(id=comment_id,status=True).first()
        if not comment_check:
            app.logger.info("Comment not found")
            return jsonify(status=400, data={}, message="Comment not found")
        
        if not (comment_check.u_id == user_id):
            delete_likes_dislikes=Opinion.query.filter_by(c_id=comment_id).all()
            if delete_likes_dislikes:
                for itr in delete_likes_dislikes:
                  db.session.delete(itr)
                  db.session.commit()
            else:
                app.logger.info("No likes or dislikes for this comment, deleting this comment ")
            comment_check.status = False
            db.session.commit()
            app.logger.info("Comment deleted successfully")
            return jsonify(status=200, data={}, message="Comment deleted successfully")
        app.logger.info("User not allowed to delete")
        return jsonify(status=404, data={}, message="User not allowed to delete")
    
    # @authentication
    def get(self):  # returning all the comments based on user_id(user comments)
        
        user_id = request.args.get('user_id')
        if not user_id:
            app.logger.info('user_id required')
            return jsonify(status=400,message="user_id required")
        
        user_obj=db.session.query(User).filter_by(id=user_id).first()
        if not user_obj:
            app.logger.info("user not found")
            return jsonify(status=404,message="user not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        
        comments_obj = db.session.query(Comments).filter_by(u_id=user_id).all()
        if not comments_obj:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")
        
        c_list = []
        for itr in comments_obj:
            dt = comments_serializer(itr)
            c_list.append(dt)

        if not c_list:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")

        page = f'/comment?user_id={user_id}'

        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                                            limit=request.args.get('limit', 3),with_params=True),
                        message="Returning queries data")

class UserGetCommentByCommentId(Resource): #getting details of comment for spefic comment
    
    # @authentication
    def get(self):
          
        comment_id=request.args.get('comment_id')
        if not (comment_id):
            app.logger.info("comment_id is required")
            return jsonify(status=404, data={}, message="comment_id is required")
       
        comment_obj = db.session.query(Comments).filter_by(id=comment_id).first()
        if not comment_obj:
            app.logger.info("No Comments found")
            return jsonify(status=404, data={}, message="No comments found")
        
        comment_data = comments_serializer(comment_obj)
        
        app.logger.info("Return comment data")
        return jsonify(status=200, data=comment_data, message="Returning comment data")