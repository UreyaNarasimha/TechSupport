from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restx import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments,SavedQueries,Opinion
from app import app, db
from sqlalchemy import or_, and_, desc, asc
from app.authentication import authentication,is_active
from app.user.serilalizer.serilalizer import query_serializer,saved_query_serializer,query_comments_serializer
from app.user.pagination.pagination import get_paginated_list
from app.utils.form_validations import title_validator,description_validator
from app.user.fileupload.file_upload import upload_file

class UserQueries(Resource):
    
    @authentication
    def post(self):

        data = request.get_json() or {}

        title = data.get('title')
        user_id = data.get('user_id')
        description = data.get('description')
        tech = data.get('technology')
        if not (title and user_id and description and tech):
            app.logger.info("title, description, user_id and technology are required")
            return jsonify(status=400, data = {}, message="title, description, user_id and technology are required")
        
        file = request.files.get('file')
 
        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=400, data = {}, message="user not found")
 
        active=is_active(user_id)
        if not active:
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, data = {}, message="User is temporarily disabled")
        
        if not title_validator(title):
            app.logger.info("Invalid title length")
            return jsonify(status=400, data = {}, message="Invalid title length")
        
        if not description_validator(description):
            app.logger.info("Invalid description length")
            return jsonify(status=400, data = {}, message="Invalid description length")
        
        tech_check = Technologies.query.filter_by(name=tech,status=True).first()
        if not tech_check:
            app.logger.info("technology not found")
            return jsonify(status=400, data = {}, message="technology not found")
        
        query_insertion = Queries.query.filter(or_(Queries.title == title,
                                                   Queries.description == description,
                                                   ),Queries.status == True).all()
        if query_insertion:
          for itr in query_insertion:
            if itr.title == title and itr.description == description:
                app.logger.info("Data already exist")
                return jsonify(status=400, data = {}, message="Data already exist")
        
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        if file:
                file_data = upload_file(self,file)
                filename =file_data[0]
                filepath =file_data[1]
        else:
                filepath = None
                filename = None
        
        question = Queries(user_id,title,description,tech_check.id,filename,filepath, date_time_obj, date_time_obj)
        db.session.add(question)
        db.session.commit()
    
        app.logger.info("Query inserted successfully")
        response = query_serializer(question)
        return jsonify(status=200, data=response, message="Query inserted successfully")
       
    @authentication
    def put(self):
        
        data = request.get_json() or {}
        
        user_id = data.get('user_id')
        query_id = data.get('query_id')
        edited_query = data.get('edited_query') #title
        technology = data.get('technology')
        description = data.get('description')
        if not(user_id and query_id and edited_query and technology and description):
            app.logger.info("user_id,query_id,technology,description and edited_query are required")
            return jsonify(status=400, data = {}, message="user_id,query_id,technology,description and edited_query are required")
        
        new_file = request.files.get('file')
        
        check_user = db.session.query(User).filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=404, data = {}, message="user not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data = {}, message="user disabled temporarily")
        
        title_check = title_validator(edited_query)
        if not title_check:
            app.logger.info("Invalid query")
            return jsonify(status=200, data = {}, message="Invalid query")
        
        description_check=description_validator(description)
        if not description_check:
            app.logger.info("Invalid description")
            return jsonify(status=200, data = {}, message="Invalid description")
        
        query_check = db.session.query(Queries).filter_by(id=query_id,status=True).first()
        if not query_check:
            app.logger.info("query not found")
            return jsonify(status=400, data = {}, message="query not found")
        
        tech_check = db.session.query(Technologies).filter_by(name=technology,status=True).first()
        if not tech_check:
            app.logger.info("technology not found")
            return jsonify(status=400, data = {}, message="technology not found")
        
        if not (query_check.u_id == user_id):
            app.logger.info("User is not allowed to edit query")
            return jsonify(status=404, data = {}, message="User is not allowed to edit query")
        if (query_check.title == edited_query and query_check.description == description):
            app.logger.info("Data already exists")
            return jsonify(status=404, data = {}, message="Data already exists")
        
        query_check.title= edited_query
        query_check.description=description
        query_check.t_id=tech_check.id
        
        if new_file:
            file_data = upload_file(self, new_file)
            new_file_name = file_data[0]
            new_file_path = file_data[1]
        else:
            new_file_name = None
            new_file_path = None
        
        query_check.filename = new_file_name
        query_check.filepath = new_file_path
        
        db.session.commit()
        app.logger.info("Comment edited")
        return jsonify(status=200, message="Comment edited",
                       data={"query_id": query_id, "edited_query": edited_query})

    @authentication
    def delete(self):
        
        query_id = request.args.get('query_id')
        user_id = request.args.get('user_id')

        if not (query_id and user_id):
            app.logger.info("Query id, user_id required to delete")
            return jsonify(status=404, data = {}, message="Query id, user_id required to delete")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()       
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=404, data = {}, message="user not found")
    
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data = {}, message="user disabled temporarily")
        
        query_check = db.session.query(Queries).filter_by(id=query_id,status=True).first()       
        if query_check:
            if not (query_check.u_id == user_id):
                saved_query = db.session.query(SavedQueries).filter_by(q_id=query_id).all()
                if saved_query:
                    for query in saved_query:
                        query.status = False
                        db.session.commit()
                delete_comment = db.session.query(Comments).filter_by(q_id=query_id).all()
                if delete_comment:
                    for itr1 in delete_comment:
                        delete_likes_dislikes=Opinion.query.filter_by(c_id=itr1.id).all()
                        for itr2 in delete_likes_dislikes:
                          db.session.delete(itr2)
                          db.session.commit()
                        itr1.status = False
                        db.session.commit()
                else:
                    app.logger.info("No comments for this query, deleting this query ")
                query_check.status = False
                db.session.commit()
                app.logger.info("Query deleted successfully")
                return jsonify(status=200, data = {}, message="Query deleted successfully")
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, data = {}, message="User not allowed to delete")

        app.logger.info("Query not found")
        return jsonify(status=400, data = {}, message="Query not found")
    
    @authentication
    def get(self):   #giving queries data based on user_id and search option
        
        query_type = request.args.get('query', None) # #getting key for search
        value = request.args.get('value', None)  
        user_id=request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=400, data = {}, message="user_id required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=404, data = {}, message="user not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data = {}, message="user disabled temporarily")
        
        queries_obj = db.session.query(Queries).filter_by(u_id=user_id,status=True).order_by(Queries.id.desc())
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, data = {}, message="No queries found")
        
        if query_type == 'search':
            queries_obj = queries_obj.filter(or_(Queries.title.ilike(f"%{value}%"),
                                                 Queries.description.ilike(f"%{value}%")
                                            ))
        # if query_type == 'sort':
        #     queries_obj.order_by(Queries.id.asc())
        
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt) 

        if not queries_list:
            app.logger.info("No results found")
            return jsonify(status=400, message = "No results found", data={})    
        
        page = f'/user/queriesbyuserid?user_id={user_id}&query={query_type}&value={value}'
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=True),
                       message="Returning queries data")

class UserGetQueryByQueryID(Resource):
    
    @authentication
    def get(self):   #giving queries data based on query id (spefic query)
        
        query_id=request.args.get('query_id')
        if not (query_id):
            app.logger.info("query_id is required")
            return jsonify(status=400, data = {}, message="query_id is required")
        
        queries_obj = db.session.query(Queries).filter_by(id=query_id,status=True).first()
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, data = {}, message="No queries found")
        
        query_data = query_comments_serializer(queries_obj)
        if not query_data:
            app.logger.info("No results found")
            return jsonify(status=400, message = "No results found", data={})    
        
        app.logger.info("Returning query data")
        return jsonify(status=200, data=query_data, message="Returning queries data")

class SaveQuery(Resource):
    
    @authentication
    def post(self):
    
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')

        if not (user_id and query_id):
            app.logger.info("query_id, user_id are required fields")
            return jsonify(status=400, data = {}, message="query_id, user_id are required fields")

        check_user = User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, data = {}, message="user not found")
        
        if not is_active(user_id):
            app.logger.info("User disabled temporarily")
            return jsonify(status=400, message="User disabled temporarily")
        
        check_query = Queries.query.filter_by(id=query_id).first()
        if not check_query:
            app.logger.info("query not found")
            return jsonify(status=400, data = {}, message="query not found")

        saved_query=SavedQueries.query.filter_by(q_id=query_id).first()
        if saved_query:
            if saved_query.status == True:  #removing if query is already saved
                saved_query.status = False
                db.session.commit()
                app.logger.info("Saved Query removed")
                return jsonify(status=200, data = {}, message="Saved Query removed")
            
            if saved_query.status == False: #saving if user previously saved and removed query
                saved_query.status = True
                db.session.commit()
                app.logger.info("Query saved")
                return jsonify(status=200, data = {}, message="Query saved")

        today = datetime.now()
        save_query = SavedQueries(user_id,query_id,True,today,today)

        db.session.add(save_query)
        db.session.commit()
        app.logger.info("Query saved")
        return jsonify(status=200, data = {}, message="Query saved")

    @authentication
    def get(self):

        user_id = request.args.get('user_id')
        if not (user_id):
            app.logger.info("user_id is required field")
            return jsonify(status=400, data = {}, message="user_id is required field")

        check_user = User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, data = {}, message="user not found")
        
        if not is_active(user_id):
            app.logger.info("User inactive")
            return jsonify(status=400, data = {}, message="User inactive")
        
        check_saved_query = SavedQueries.query.filter_by(u_id=user_id,status=True).all()
        if not check_saved_query:
            app.logger.info("no data found")
            return jsonify(status=400, data = {}, message="no data found")

        saved_query_list=[]
        for itr in check_saved_query:
            dt=saved_query_serializer(itr)
            saved_query_list.append(dt)
        if not saved_query_list:
            app.logger.info("no data found")
            return jsonify(status=400, data = {}, message="no data found")
        
        page = f"/save?user_id={user_id}"     
        app.logger.info("Returning saved queries")
        return jsonify(status=200, data=get_paginated_list(saved_query_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning saved queries data")
        


    