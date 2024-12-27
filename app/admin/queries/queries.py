from flask import jsonify, request
from flask_restx import Resource
from datetime import datetime
from sqlalchemy.sql.expression import delete
from app.user.models.models import User, Queries, Comments, Opinion, SavedQueries
from app import app, db
from app.authentication import encode_auth_token,authentication,is_active
from app.user.serilalizer.serilalizer import query_serializer, query_comments_serializer
from app.user.pagination.pagination import get_paginated_list
from sqlalchemy import or_, and_, desc, asc

class AdminQueries(Resource):
    
    @authentication
    def put(self):
        
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        title = data.get('title')
        description = data.get('description')

        if not (query_id and user_id and title and description):
            app.logger.info("Query id , User id , title , description are required fields")
            return jsonify(status=400, data={},
                           message="Query id , User id , title , description are required fields")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("User not allowed to update queries")
            return jsonify(status=404, data={}, message="User not allowed to update queries")
        
        query_check = db.session.query(Queries).filter_by(id=query_id,status=True).first()
        if not query_check:
            app.logger.info("query not found")
            return jsonify(status=400, data={}, message="query not found")
        
        query_check.title = title
        query_check.description = description
        db.session.commit()

        app.logger.info("Query edited")
        return jsonify(status=200, message="Query edited",
                       data={"query_id": query_id, "title": title, "description": description})

    @authentication
    def delete(self):
               
        query_id = request.args.get('query_id')
        user_id = request.args.get('user_id')
        if not (query_id and user_id):
            app.logger.info("query_id and user_id are required")
            return jsonify(status=404, data={}, message="query_id and user_id are required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
                    app.logger.info("user not found")
                    return jsonify(status=404, data={}, message="user not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("User not allowed to delete queries")
            return jsonify(status=404, data={}, message="User not allowed to delete queries")
        
        query_check = db.session.query(Queries).filter_by(id=query_id,status=True).first()
        if not query_check:
            app.logger.info("Query not found")
            return jsonify(status=404, data={}, message="Query not found")
        
        saved_query = db.session.query(SavedQueries).filter_by(q_id=query_id).all()
        if saved_query:
            for itr in saved_query:
                saved_query.status = False
                db.session.commit()
        delete_comment = db.session.query(Comments).filter_by(q_id=query_id).all()
        if delete_comment:
            for itr in delete_comment:
                delete_likes_dislikes_comment = Opinion.query.filter_by(c_id=itr.id).all()
                for itr2 in delete_likes_dislikes_comment:
                    db.session.delete(itr2)
                    db.session.commit()
                delete_comment.status = False
                db.session.commit()
        else:
            app.logger.info("No comments for this query, deleting this query ")
        query_check.status = False
        db.session.commit()
        app.logger.info("Query deleted successfully")
        return jsonify(status=200, data={}, message="Query deleted successfully")
       
    @authentication
    def get(self):  # send all the queries

        query_type = request.args.get('query', None) # #getting key for search
        value = request.args.get('value', None) 
        user_id = request.args.get('user_id')
        if not user_id:
            app.logger.info("User id is required field")
            return jsonify(status=400, data={},
                            message="User id is required field")

        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")

        query_objs = db.session.query(Queries).order_by(Queries.updated_at)
        if not query_objs:
            app.logger.info("No records found")
            return jsonify(status=404, data={}, message="No records found")
        
        if query_type == 'search':
            queries_obj = queries_obj.filter(or_(Queries.title.ilike(f"%{value}%"),
                                                 Queries.description.ilike(f"%{value}%")
                                            ))

        c_list = []
        for itr in query_objs:
            dt = query_serializer(itr)
            c_list.append(dt)

        page = f'/admin/queries?user_id={user_id}'

        app.logger.info("Return queries data")
        return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3), with_params=False),
                       message="Returning queries data")
    
class AdminGetQueryByQueryId(Resource):   #returning spefic query details
    
    @authentication
    def get(self):
        
        query_id=request.args.get('query_id')
        if not query_id:
            app.logger.info("query_id is required")
            return jsonify(status=400, data={}, message="query_id is required")

        query_obj = db.session.query(Queries).filter_by(id=query_id).first()
        if not query_obj:
            app.logger.info("No records found")
            return jsonify(status=404, data={}, message="No records found")
    
        data = query_comments_serializer(query_obj)  
        app.logger.info("Returning query data")
        return jsonify(status=200, data=data, message="Returning query data")

class AdminGetQueryByUserId(Resource):  #returning queries based on user_id
    
    @authentication
    def get(self):
        
        query_type = request.args.get('query', None) # #getting key for search
        value = request.args.get('value', None)
        user_id=request.args.get('user_id')
        requested_user_id = request.args.get('requested_user_id')
        if not (user_id and requested_user_id):
            app.logger.info("user_id, requested_user_id are required")
            return jsonify(status=400, data={}, message="user_id, requested_user_id are required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")
        
        requested_user_check = db.session.query(User).filter_by(id=requested_user_id,status=True).first()
        if not requested_user_check:
            app.logger.info("Requested User not found")
            return jsonify(status=400, data={}, message="Requested User not found")

        queries_obj = db.session.query(Queries).filter_by(u_id=requested_user_id)
        if not queries_obj:
            app.logger.info("No records found")
            return jsonify(status=404, data={}, message="No records found")
        
        if query_type == 'search':
            queries_obj = queries_obj.filter(or_(Queries.title.ilike(f"%{value}%"),
                                                 Queries.description.ilike(f"%{value}%")
                                            ))
        
        queries_list=[]
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        
        page = f'/admin/querybyuserid?user_id={user_id}&requested_user_id={requested_user_id}'
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                          limit=request.args.get('limit', 3), with_params = False), message="Returning queries data")

class Unanswered(Resource):
    
    # @authentication
    def get(self):

        user_id=request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=400, data={}, message="user_id required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")

        unanswered_queries_obj_list = []
        unanswered_queries_list = []
        
        r = db.session.query(Queries, Comments).outerjoin(Comments, Queries.id == Comments.q_id).all()
        if not r:
            app.logger.info("no records found")
            return jsonify(status=404, data={}, message="no records found")

        for result in r:
            if not result[1]:
                unanswered_queries_obj_list.append(result[0])

        if not unanswered_queries_obj_list:
            app.logger.info("no records found")
            return jsonify(status=404, data={}, message="no records found")

        for itr in unanswered_queries_obj_list:
            dt = query_serializer(itr)
            unanswered_queries_list.append(dt)
        
        page = f'/unanswered?user_id={user_id}'
        app.logger.info("Returning queries data")
        return jsonify(status=200,data=get_paginated_list(unanswered_queries_list, page, start=request.args.get('start', 1),
                                          limit=request.args.get('limit', 3),with_params = False),
                                          message="Returning unanswered queries data")

