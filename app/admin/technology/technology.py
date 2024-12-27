from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restx import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments
from app import app, db
from sqlalchemy import or_, and_, desc
from app.authentication import encode_auth_token, authentication,is_active
from app.user.serilalizer.serilalizer import technology_serializer,replace_with_ids
from app.user.pagination.pagination import get_paginated_list


class Technology(Resource):
    
    @authentication
    def post(self):
        
        data = request.get_json() or {}
        
        user_id = data.get('user_id')
        technologies = data.get('technologies')
        if not (user_id and technologies):
            app.logger.info("User_id and technologies are required")
            return jsonify(status=404, data={}, message="User_id and technologies are required")
        
        check_user = User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to add technologies")
            return jsonify(status=404, data={}, message="User not allowed to add technologies")
        
        for itr in technologies:
            check_tech_exist = Technologies.query.filter_by(name=itr,status=True).first()
            if check_tech_exist:
                app.logger.info(f"{itr} technology already exists")
                return jsonify(status=400, data={}, message=f"{itr} technology already exists")
        
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        for itr in technologies:
            tech = Technologies(itr, date_time_obj, date_time_obj)
            db.session.add(tech)
            db.session.commit()
        return jsonify(status=200, data={}, message="Technologies added successfully")

    @authentication
    def put(self):
        
        data = request.get_json() or {}
        user_id = data.get('user_id')
        tech_id = data.get('technology_id')
        technology_name = data.get('technology_name')
        
        if not (user_id and tech_id and technology_name):
            app.logger.info("User_id, technology_id and technology_name are required")
            return jsonify(status=404, data={}, message="User_id, technology_id and technology_name are required")
        
        check_user = User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to update technologies")
            return jsonify(status=404, data={}, message="User not allowed to update technologies")
        
        check_tech = Technologies.query.filter_by(name=technology_name,status=True).first()
        if not check_tech:
            app.logger.info("Technology not found")
            return jsonify(status=400, data={}, message="Technology not found")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')

        check_tech.name = technology_name
        check_tech.updated_at = date_time_obj
        db.session.commit()
        return jsonify(status=200, data={}, message="Technology updated successfully")

    @authentication
    def get(self):  #returning all technologues

        query_type = request.args.get('query', None) # #getting key for search
        value = request.args.get('value', None)  
        user_id = request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id is required")
            return jsonify(status=404, data={}, message="user_id is required")
        
        check_user = User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")

        technology_objs = db.session.query(Technologies).order_by(Technologies.updated_at)
        if not technology_objs:
            app.logger.info("No Technologies in DB")
            return jsonify(status=404, data={}, message="No Technologies in DB")
        
        if query_type == 'search':
            technology_objs = technology_objs.filter(Technologies.name.ilike(f"%{value}%"))
        
        t_list = []
        for itr in technology_objs:
             dt = technology_serializer(itr)
             t_list.append(dt)

        if not t_list:
            app.logger.info("No Technologies in DB")
            return jsonify(status=404, data={}, message="No Technologies in DB")

        page = f'/technology?user_id={user_id}'
        app.logger.info("Return Technologies data")
        return jsonify(status=200, data=get_paginated_list(t_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3), with_params=False),
                       message="Returning Technologies data")

    @authentication
    def delete(self):
               
        technology_id = request.args.get('technology_id')
        user_id = request.args.get('user_id')
        if not (technology_id and user_id):
            app.logger.info("technology_id, user_id required to delete")
            return jsonify(status=404, data={}, message="technology_id, user_id required to delete")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("User not allowed to delete technologies")
            return jsonify(status=404, data={}, message="User not allowed to delete technologies")
        
        tech_check = db.session.query(Technologies).filter_by(id=technology_id).first()
        if tech_check:
            if tech_check.status == True:
                tech_check.status = False
                db.session.commit()
                app.logger.info("Technology deactivated successfully")
                return jsonify(status=200, data={}, message="Technology deactivated successfully")
            if tech_check.status == False:
                tech_check.status = True
                db.session.commit()
                app.logger.info("Technology activated successfully")
                return jsonify(status=200, data={}, message="Technology activated successfully")
        app.logger.info("Technology not found")
        return jsonify(status=400, message="Technology not found")

class GetTechnologybyTechnologyid(Resource):

    @authentication
    def get(self):  #returning technology details based on technology id

        technology_id = request.args.get('technology_id')
        if not technology_id:
            app.logger.info("technology_id is required feild")
            return jsonify(status=404, data={}, message="technology_id is required feild")

        technology_obj = db.session.query(Technologies).filter_by(id=technology_id,status=True).first()
        if not technology_obj:
            app.logger.info("No Technologies in DB")
            return jsonify(status=404, data={}, message="No Technologies in DB")
        
        data = technology_serializer(technology_obj)

        app.logger.info("Return Technology data")
        return jsonify(status=200, data=data, message="Returning Technology data")
