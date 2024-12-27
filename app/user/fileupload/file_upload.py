from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app
from flask_restx import Resource
from app.user.models.models import db
import os
from flask import send_from_directory
import os
from app.user.models.models import User,Comments,Queries
from app.authentication import authentication,is_active

class download(Resource): #downloading file
  
  def get(self):
      
      data=request.get_json() or {}
      
      user_id=data.get('user_id')
      comment_id=data.get('comment_id')
      query_id=data.get('query_id')
      if not (user_id and (comment_id or query_id)):
          app.logger.info('user_id and comment_id or query_id are required')
          return jsonify(status=400, message='user_id and comment_id or query_id are required')
      
      user_check = User.query.filter_by(id=user_id).first()
      if not user_check:
        app.logger.info('user not found')
        return jsonify(status=400, message="user not found")
      
      active = is_active(user_id)
      if not active:
        app.logger.info("user disabled temporarily")
        return jsonify(status=400, data={}, message="user disabled temporarily")
      
      cwd = os.getcwd()
      folder = "UPLOAD"
      path = os.path.join(cwd, folder)
      
      if comment_id:
         comment_check = Comments.query.filter_by(id=comment_id).first()
         if not comment_check:
            app.logger.info('comment not found')
            return jsonify(status=400, message="comment not found")
         try:
           file=Comments.query.filter(Comments.id==comment_id).first()
           filename=file.filename
           return send_from_directory(path,filename)
         except:
           app.logger.info("No records found")
           return jsonify(status=200,message="No records found")
      elif query_id:
          query_check = Queries.query.filter_by(id=query_id).first()
          if not query_check:
              app.logger.info('query not found')
              return jsonify(status=400, message="query not found")
          try:
              file = Queries.query.filter(Queries.id == query_id).first()
              filename = file.filename
              return send_from_directory(path, filename)
          except:
              app.logger.info("No records found")
              return jsonify(status=200, message="No records found")


def upload_file(self,file):  #file uploading
  
    cwd = os.getcwd()
    folder = "UPLOAD"
    path = os.path.join(cwd, folder)
    if not os.path.exists(path):
       os.mkdir(path)
    if not file:
        app.logger.info('file required')
        return jsonify(status=400, message="file required")
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(path, filename))
        path = f'{path}/{filename}'
        return filename,path
    return


