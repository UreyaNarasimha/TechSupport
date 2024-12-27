from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restx import Resource
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.user.models.models import User, Roles
from app import app, db
from sqlalchemy import or_,and_,desc
from app.authentication import encode_auth_token,authentication, is_active
from app.user.serilalizer.serilalizer import user_serializer, role_serializer
from app.user.pagination.pagination import get_paginated_list
from app.utils.smtpmail import send_mail_to_reset_password

class AdminLogin(Resource):
    
    def post(self):
    
        data = request.get_json() or {}
        email=data.get("email")
        mobile=data.get("mobile")
        password=data.get('password')
        if not ((email or mobile) and password):
            app.logger.info("email or mobile and password are required")
            return jsonify(status=400, data={}, message="email or mobile and password are required")
        
        user = db.session.query(User).filter(or_(User.email == email, User.mobile == mobile)).first()
        if user:
            if user.roles!=1:
                if check_password_hash(user.password, password):
                    token = encode_auth_token(user)
                    app.logger.info(token)
                    response = user_serializer(user)
                    app.logger.info(f'{user.name} Logged in successfully')
                    return jsonify(status=200, data=response, message="Logged in successfully",
                                   token=token)
                else:
                    app.logger.info(f"{user.name} Incorrect password")
                    return jsonify(status=400, data={}, messsage="Incorrect password")
            else:
                app.logger.info(f"{user.name} Not allowed to login as admin")
                return jsonify(status=400, data={}, messsage="Not allowed to login as admin")
        else:
            app.logger.info(f"user not found")
            return jsonify(status=400, data={}, message="user not found")

class AdminForgotPassword(Resource):
    
    def post(self):
        
        data = request.get_json()
        email = data.get("email")
        mobile = data.get("mobile")

        if not (email and mobile):
            app.logger.info("email, mobile fields are required")
            return jsonify(status=400, data={}, message="email, mobile fields are required")

        user = db.session.query(User).filter(and_(User.email == email, User.mobile == mobile)).first()
        if not user:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")
        
        active = is_active(user.id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")

        try:
            if user and user.roles!=1:
                new_password = send_mail_to_reset_password(user.email, user.name)
                if new_password == 'Error':
                    app.logger.info("mail sending failed")
                    return jsonify(status=400,data={}, message="mail sending failed")
                app.logger.info("Email sent successfully")
                today = datetime.now()
                date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                user.updated_at = date_time_obj
                user.password = generate_password_hash(new_password, method='sha256')
                db.session.commit()
                app.logger.info(f'{user.name} password changed  successfully')
                return jsonify(status=200, data={}, message="password changed  successfully")
            app.logger.info("cannot change password")
            return jsonify(status=400, data={}, message="cannot change password")
        except:
            app.logger.info("database error")
            return jsonify(status=400, data={}, message="database error")

class UserDelete(Resource):
    
    @authentication
    def delete(self):  #for activating and deactivating user 
        
        user_id = request.args.get('user_id')
        delete_user = request.args.get('delete_user_id')
        if not (delete_user and user_id):
            app.logger.info("delete_user_id and User id are required fields")
            return jsonify(status=400, data={}, message="delete_user_id and User id are required fields")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")

        delete_user = db.session.query(User).filter_by(id=delete_user).first()
        if not delete_user:
            app.logger.info("User wanted to delete not found")
            return jsonify(status=400, data={}, message="User wanted to delete not found")
        
        try:
            if delete_user.status == 1:
                delete_user.status = 0  # changed from roles to status (soft delete)
                today = datetime.now()
                date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                delete_user.updated_at = date_time_obj
                db.session.commit()
                app.logger.info(f"user disabled successfully")
                return jsonify(status=200, data={}, message=f"user disabled successfully")
            else:
                delete_user.status = 1  # changed from roles to status (soft delete)
                today = datetime.now()
                date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                delete_user.updated_at = date_time_obj
                db.session.commit()
                app.logger.info("user activated successfully")
                return jsonify(status=200, data={}, message="user activated successfully")
        except:
            app.logger.info("something went wrong")
            return jsonify(status=400, data={}, message= "something went wrong")

class GetProfile(Resource): #getting user details based on user_id
    
    @authentication
    def get(self):

        profile_user_id = request.args.get('profile_user_id')
        if not (profile_user_id):
            app.logger.info("profile_user_id is required")
            return jsonify(status=400, data={}, message="profile_user_id is required")
        
        profile_user_data = db.session.query(User).filter_by(id=profile_user_id).first()
        if not profile_user_data:
            app.logger.info("requested profile user not found")
            return jsonify(status=400, data={}, message="requested profile user not found")
        
        return jsonify(status=200,data=user_serializer(profile_user_data),message="user data")

class GetAllUsers(Resource): #getting all users
    
    @authentication
    def get(self):

        query_type = request.args.get('query', None) # getting key for search
        value = request.args.get('value', None)
        user_id = request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id is required")
            return jsonify(status=400, data={}, message = "user_id is required" )
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")
    
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")
        
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("Insufficient Privileges")
            return jsonify(status=404, data={}, message="Insufficient Privileges")
        
        users = db.session.query(User)
        if not users:
            app.logger.info("No users found")
            return jsonify(status=400, data={}, message="No users found")
        
        if query_type == 'search':
            users = users.filter(or_(User.email.ilike(f"%{value}%"),
                                    User.name.ilike(f"%{value}%"),
                                    User.mobile.ilike(f"%{value}%"),
                                    User.roles.ilike(f"%{value}%")
                                            ))
        
        users_list=[]
        for itr in users:
            dt = user_serializer(itr)
            users_list.append(dt)
        
        page = f'/admin/getallusers?user_id={user_id}'
        return jsonify(status=200, data=get_paginated_list(users_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3), with_params=False),
                       message="Returning all user's name and ids")

class AdminRoles(Resource):

    @authentication
    def post(self): #add new role
        
        data=request.get_json() or {}

        new_role=data.get('new_role')
        user_id=data.get('user_id')
        
        if not (new_role and user_id):
            app.logger.info("new_role and user_id are required fields")
            return jsonify(status=400, data={}, message="new_role and user_id are required fields")
        
        check_super_admin=User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")
        
        if check_super_admin.roles == 3:
            check_role_exists=Roles.query.filter(Roles.name.ilike(f"{new_role}")).first()
            if check_role_exists:
                app.logger.info("role already exists")
                return jsonify(status=400, data={}, message="role already exists")
            
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            add_role = Roles(new_role, True, date_time_obj, date_time_obj)
            db.session.add(add_role)
            db.session.commit()
            app.logger.info("role added succesfully")
            return jsonify(status=200, message="role added succesfully")
        app.logger.info("user is not allowed to add new roles")
        return jsonify(status=400, message="user is not allowed to add new roles")
    
    @authentication 
    def put(self): #edit new role
        
        data = request.get_json() or {}
        edited_role = data.get('edited_role')
        role_id=data.get('role_id')
        user_id = data.get('user_id')

        if not (user_id and edited_role and role_id):
            app.logger.info("user_id,edited_role, role_id are required fields")
            return jsonify(status=400, data={}, message="user_id,edited_role, role_id are required fields")

        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")

        if check_super_admin.roles == 3:
            check_role_exists = Roles.query.filter_by(id=role_id).first()
            if check_role_exists:
                check_role_exists.name=edited_role
                db.session.commit()
                app.logger.info("role edited")
                return jsonify(status=200, data={}, message="role edited")
            app.logger.info("role not found")
            return jsonify(status=400, data={}, message="role not found")
        app.logger.info("only superadmin can make changes")
        return jsonify(status=400, data={}, message="only superadmin can make changes")
    
    @authentication
    def get(self): #get all roles

        query_type = request.args.get('query', None) # getting key for search
        value = request.args.get('value', None)
        user_id = request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id is required")
            return jsonify(status=400, data={}, message="user_id is required")
        
        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")

        if check_super_admin.roles == 3:
            
            list_of_roles=[]
            get_roles = db.session.query(Roles)
            
            if query_type == 'search':
                get_roles = get_roles.filter(Roles.name.ilike(f"%{value}%"))

            for itr_role in get_roles:
                list_of_roles.append(role_serializer(itr_role))
            
            page = f'/admin/roles?user_id={user_id}'
            return jsonify(status=200, data=get_paginated_list(list_of_roles, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3), with_params=False),
                       message="Roles data")

        app.logger.info("only superadmin can make changes")
        return jsonify(status=400, data={}, message="only superadmin can make changes")
    
    @authentication
    def delete(self):

        role_id = request.args.get('role_id')
        user_id = request.args.get('user_id')
        if not (user_id and role_id):
            app.logger.info("user_id and role_id are required")
            return jsonify(status=400, data={}, message="user_id and role_id are required")
        
        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")

        if check_super_admin.roles == 3:
            check_role_exists = Roles.query.filter_by(id=role_id).first()
            if check_role_exists:
                if check_role_exists.status == 1:
                    check_role_exists.status = 0
                    message = "role deactivated"
                else:
                    check_role_exists.status = 1
                    message = "role activated"
                db.session.commit()
                app.logger.info(message)
                return jsonify(status=400, data={}, message=message)
        
        app.logger.info("only superadmin can delete")
        return jsonify(status=400, data={}, message="only superadmin can delete")

class UserRoleUpdate(Resource): #changing user roles
    
    @authentication
    def put(self):
    
        data = request.get_json() or {}
        user_id = data.get('user_id')
        change_user_id = data.get('change_user_id')
        change_user_role = data.get('change_user_role')
        if not (change_user_id and user_id and change_user_role):
            app.logger.info("change_user_id and user id and change_user_role are required fields")
            return jsonify(status=400, data={}, message="change_user_id and user id and change_user_role are required fields")

        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=400, data={}, message="admin disabled temporarily")

        change_role_user_id_check = db.session.query(User).filter_by(id=change_user_id).first()
        if not change_role_user_id_check:
            app.logger.info("User you wanted to change role not found")
            return jsonify(status=400, data={}, message="User you wanted to change role not found")
        
        role_check = db.session.query(Roles).filter_by(id=change_user_role).first()
        if not role_check:
            app.logger.info("Role not found")
            return jsonify(status=400, data={}, message="Role not found")

        if user_check.roles == 3:
            change_role_user_id_check.roles = change_user_role
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            change_role_user_id_check.updated_at = date_time_obj
            db.session.commit()
            app.logger.info("role changed successfully")
            return jsonify(status=200, data={}, message="role changed successfully")
        
        app.logger.info("User not allowed to perform this action")
        return jsonify(status=400, data={}, message="User not allowed to perform this action")