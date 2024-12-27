from datetime import datetime, timedelta
import jwt
from app import app
import os, ast
from flask import request, jsonify
from app.user.models.models import User
from functools import wraps

def deserialize_to_json(user_data):
    
    return {
        "user_id":user_data.id,
        "user_name":user_data.name,
        "email":user_data.email,
        "mobile":user_data.mobile,
        "technology":user_data.technology
        }

def encode_auth_token(user):
    """
    Generates the Auth Tokens: access token and refresh token.
    :param user: The user object to serialize
    :return: tuple (access_token, refresh_token)
    """
    try:
        # Define the payload for both tokens
        access_token_payload = {
            'exp': datetime.utcnow() + timedelta(hours=1),  # Short expiry for access token
            'iat': datetime.utcnow(),
            'sub': str(deserialize_to_json(user))
        }

        refresh_token_payload = {
            'exp': datetime.utcnow() + timedelta(days=30),  # Longer expiry for refresh token
            'iat': datetime.utcnow(),
            'sub': str(deserialize_to_json(user))
        }

        # Generate the access token
        access_token = jwt.encode(
            access_token_payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

        # Generate the refresh token
        refresh_token = jwt.encode(
            refresh_token_payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

        token = {
            "access_token" : access_token,
            "refresh_token" : refresh_token
        }

        # Return both tokens
        return token
    
    except Exception as e:
        return str(e)

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """

    if not auth_token:
        return False, 'Authorization header is missing.'

    parts = auth_token.split()
    
    # Check if the token is in 'Bearer <token>' format
    if len(parts) != 2 or parts[0] != 'Bearer':
        return False, 'Invalid Token'
    
    auth_token = parts[1]
    
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms=["HS256"])
        return True, payload['sub']
    except jwt.ExpiredSignatureError:
        return False, 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return False, 'Invalid token. Please log in again.'

def authentication(func):
    
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        try:
            is_valid, token = decode_auth_token(request.headers['token'])
        except:
            return jsonify(status=404,message="Token required")
        if is_valid:
            return func(*args, **kwargs)
        return jsonify(status=401,message=token)
    return decorated

def get_user_id(self):
    token = ast.literal_eval(decode_auth_token(request.headers['token'])[1])
    return token.get('user_id')

def is_active(user_id):
    
    check_status=User.query.filter_by(id=user_id).first()
    return check_status.status


