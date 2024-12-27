from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restx import Resource
from datetime import datetime
from app.user.models.models import User,Technologies
from app import app, db
from sqlalchemy import or_, and_, desc
import re
from werkzeug.security import generate_password_hash, check_password_hash
from app.authentication import encode_auth_token, authentication
from app.user.serilalizer.serilalizer import user_serializer,replace_with_ids
from app.user.pagination.pagination import get_paginated_list
from app.utils.smtpmail import send_mail_to_reset_password,generate_temp_password_and_check
from app.utils.form_validations import name_validator,password_validator,email_validator,number_validation,title_validator
from app.authentication import get_user_id,authentication,is_active


class Login(Resource):
    
    def post(self):
    
        data = request.get_json() or {}
        email = data.get("email")
        mobile = data.get("mobile")
        password = data.get('password')
        if not ((email or mobile) and password):
            app.logger.info("email or mobile and password are required")
            return jsonify(status=400, data={}, message="email or mobile and password are required")
        user = db.session.query(User).filter(or_(User.email == email, User.mobile == mobile)).first()
        if user:
            if user.status == 0:
                app.logger.info("User is disabled temporarily")
                return jsonify(status=400, data={}, message="User is disabled temporarily")
            if check_password_hash(user.password, password):
                token = encode_auth_token(user)
                app.logger.info(token)
                response = user_serializer(user)
                User.login=True
                db.session.commit()
                app.logger.info(f'{user.name} Logged in successfully')
                return jsonify(status=200, data=response, message="Logged in successfully", token=token)
            else:
                app.logger.info(f"{user.name} Incorrect password")
                return jsonify(status=404, data={}, messsage="Incorrect password")
        else:
            app.logger.info(f"user not found")
            return jsonify(status=404, data={}, message="user not found")

class Logout(Resource):
    
    def post(self):
        app.logger.info("Logged out successfully")
        return jsonify(status=200, data={}, message="Logged out successfully")

class Register(Resource):
    
    def post(self):
        
        data = request.get_json()
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        
        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')
        list_of_tech = data.get('technology')
        password = data.get("password")
        
        if not (name and email and mobile and list_of_tech and password):
            msg = 'name, email, mobile, technology and password are required fields'    
            app.logger.info(msg)
            return jsonify(status=400, data={}, message=msg)
        elif not name_validator(name): # check valid name
            msg = 'Invalid name' 
            app.logger.info(msg)
            return jsonify(status=400, data={}, message=msg)
        elif not email_validator(email): # check valid email
            msg = 'Invalid email address'
            app.logger.info(msg)
            return jsonify(status=400, data={}, message=msg)
        elif not number_validation(mobile): #check valid mobile number
            msg = 'Invalid phone number'
            app.logger.info(msg)
            return jsonify(status=400, data={}, message=msg)
        elif not password_validator(password): #check valid password
            msg = 'Invalid password'
            app.logger.info(msg)
            return jsonify(status=400, data={}, message=msg)
        else:     
            try:
                user = User.query.filter(or_(User.email == email,
                                             User.mobile == mobile)).first()
                if user:
                    if user.status == False:
                        msg = 'User disabled temporarily'
                        app.logger.info(msg)
                        return jsonify(status=400, data={}, message=msg)
                    msg = 'User already exist'
                    app.logger.info(msg)
                    return jsonify(status=400, data={}, message=msg)
                
                else:
                    ids_list = f"{replace_with_ids(list_of_tech)}"
                    today = datetime.now()
                    date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                    password = generate_password_hash(password)
                    status=True
                    user = User(name, email, mobile, ids_list, password,status,date_time_obj, date_time_obj)
                    db.session.add(user)
                    db.session.commit()
                    response = {"name": name, "email": email, "mobile": mobile, "technology": list_of_tech}
                    app.logger.info(f'{user.name} Registered successfully')
                    return jsonify(status=200, data=response, message="Registered successfully")
            except:
                app.logger.info("Database connection not established")
                return jsonify(status=404, data={}, message="Database connection not established")
        
class UpdatePassword(Resource):
    
    @authentication
    def put(self):
        
        data = request.get_json() or {}
        
        email = data.get("email")
        mobile = data.get("mobile")
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")
        user_id = data.get("user_id")
        
        if not (user_id and (email or mobile) and (old_password and new_password and confirm_new_password)):
            app.logger.info(f'user_id, email (or) mobile , old_password, new_password and confirm_new_password required')
            return jsonify(status=400, data={},
                           message="user_id, email (or) mobile , old_password, new_password and confirm_new_password required")
        
        if not password_validator(new_password):
            msg = 'Invalid password'
            app.logger.info(msg)
            return jsonify(status=400,message=msg)
        
        try:
            user = db.session.query(User).filter(or_(User.email == email, User.mobile == data.get("mobile"))).first()
            if user:
                active = is_active(user_id)
                if not active:
                    app.logger.info("user disabled temporarily")
                    return jsonify(status=400, data={}, message="user disabled temporarily")
                
                if check_password_hash(user.password, data.get('old_password')):
                    if new_password == confirm_new_password:
                        if new_password == old_password:
                            app.logger.info("New password and old password should not be same")
                            return jsonify(status=400, message="New password and old password should not be same")
                        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$',
                                        new_password):
                            app.logger.info(
                                "Password should contain min 8 characters, a special character, Uppercase, lowercase and a number")
                            return jsonify(status=400, data={},
                                           message='Password should contain min 8 characters, a special character, Uppercase, lowercase and a number')
                        user.password = generate_password_hash(new_password)
                        db.session.commit()
                        app.logger.info(f'{user.name} Password updated successfully')
                        return jsonify(status=200, data={}, message="Password updated successfully")
                    else:
                        app.logger.info(f'{user.name} New password and confirm new password doesnt match')
                        return jsonify(status=200, data={}, message="New password and confirm new password doesn't match")
                else:
                    app.logger.info(f"{user.name} Incorrect old password")
                    return jsonify(status=404, data={}, message="Incorrect old password")
            else:
                app.logger.info("User not found")
                return jsonify(status=404, data={}, message="User not found")
        except:
            app.logger.info("Unknown database")
            return jsonify(status=404, data={}, message="Unknown database")

class ForgotPassword(Resource):
    
    def post(self):
        
        data = request.get_json() or {}
        
        email = data.get("email")
        mobile = data.get("mobile")

        if not (email and mobile):
            app.logger.info("email and mobile fields are required")
            return jsonify(status=400, data={}, message="email and mobile fields are required")
        
        user = db.session.query(User).filter(and_(User.email == email, User.mobile == mobile)).first()
        if not user:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")
        
        active = is_active(user.id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data={}, message="user disabled temporarily")
        
        new_password = send_mail_to_reset_password(user.email, user.name)
        if new_password == 'Error':
            app.logger.info("mail sending failed")
            return jsonify(status=400, data={}, message="mail sending failed")
        
        app.logger.info(f"Email sent successfully to {user.email}")
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        user.updated_at = date_time_obj
        user.password = generate_password_hash(new_password)
        db.session.commit()
        app.logger.info(f'{user.name} password changed  successfully')
        return jsonify(status=200, data={}, message="password changed  successfully")
            
class UserProfile(Resource):
    
    @authentication
    def get(self):    #user details 
        
        user_id=get_user_id(self)
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=400, data={}, message="user_id required") 
        
        user_data=db.session.query(User).filter_by(id=user_id).first()
        if not user_data:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data={}, message="user disabled temporarily")
        
        return jsonify(status=200,data=user_serializer(user_data),message="user data")
    
    @authentication
    def put(self): #update user data
        
        data = request.get_json() or {}
        
        user_id=data.get('user_id')
        name = data.get('name')
        technology = data.get('technology')

        if not (user_id and name and technology):
            app.logger.info("user_id, name and technology are required")
            return jsonify(status=400, data={}, message="user_id, name and technology are required")
        
        if not name_validator(name):
            msg = 'Invalid name'
            app.logger.info(msg)
            return jsonify(status=404,message=msg)
        
        user_update=db.session.query(User).filter_by(id=user_id).first()
        if not user_update:
            app.logger.info("user not found")
            return jsonify(status=400, data={}, message="user not found")
        
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, data={}, message="user disabled temporarily")
        else:
            if user_update:
                if not user_update.name == name:
                    user_update.name = name
                else:
                 app.logger.info("new name should be taken")
                 return jsonify(status=400, data={}, message="new name should be taken")
                tech_list=[]
                for itr in technology:
                    tech_check=Technologies.query.filter_by(name=itr).first()
                    if tech_check:
                        tech_list.append(tech_check.id)
                user_update.technology=f"{tech_list}"
                today = datetime.now()
                user_update.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                db.session.commit()
                response = {"name": user_update.name, "technology": technology}
                app.logger.info(f'{user_update.name} Updated successfully')
                return jsonify(status=200, data=response, message="updated Successfully")

class UserStatus(Resource): #activating and deactivating user

    @authentication
    def delete(self):

        user_id = request.args.get('user_id')

        if not (user_id):
            app.logger.info("user_id required")
            return jsonify(status=404, data={}, message="user_id required")
        
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, data={}, message="User not found")
               
        if user_check.status == 1:
            user_check.status = 0
            msg = 'user activated successfully'
        else:
            user_check.status = 1
            msg = 'user deactivated successfully'
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        user_check.updated_at = date_time_obj
        db.session.commit()
        app.logger.info(msg)
        return jsonify(status=200, data={}, message=msg)
    
