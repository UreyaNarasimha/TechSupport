
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restx import Api
# from flask_cors import CORS
from flask_migrate import Migrate

# from OpenSSL import SSL
# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'rmijlkqqqawtre@1((11'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mysql#123@localhost/tech_support'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
migrate=Migrate(app,db)
api = Api(app)

with app.app_context():
    db.create_all() 

from app.user.queries.queries import UserQueries, UserGetQueryByQueryID, SaveQuery
from app.user.comments.comments import UserComment,UserGetCommentByCommentId
from app.user.user.user import Register,Logout,UpdatePassword,ForgotPassword,UserProfile, UserStatus,Login
from app.user.opinion.like import Like,DisLike
from app.user.fileupload.file_upload import download

from app.admin.technology.technology import Technology, GetTechnologybyTechnologyid
from app.admin.comments.comments import AdminComment,AdminGetCommentsByUserId,AdminGetCommentsByCommentId
from app.admin.queries.queries import AdminQueries,AdminGetQueryByUserId,AdminGetQueryByQueryId
from app.admin.queries.queries import Unanswered
from app.admin.users.users import AdminRoles,GetAllUsers,GetProfile,UserDelete,UserRoleUpdate,AdminForgotPassword,AdminLogin

#user 
api.add_resource(Login, "/login")
api.add_resource(Register,"/register")
api.add_resource(Logout,"/logout")
api.add_resource(UpdatePassword,"/changepassword")
api.add_resource(ForgotPassword,"/forgotpassword")
api.add_resource(UserProfile,"/profile")
api.add_resource(UserStatus,"/userstatus")

#query
api.add_resource(UserQueries,"/query")
api.add_resource(UserGetQueryByQueryID,"/user/querybyqueryid")

#comment
api.add_resource(UserComment,"/comment")
api.add_resource(UserGetCommentByCommentId,"/user/commentbycommentid")

#opinion
api.add_resource(Like,"/like")
api.add_resource(DisLike,"/dislike")
api.add_resource(download,"/download")

#save
api.add_resource(SaveQuery,"/save")

#admin technology
api.add_resource(Technology,"/technology")
api.add_resource(GetTechnologybyTechnologyid,"/technologybytechnologyid")

#admin queries
api.add_resource(AdminQueries,"/admin/queries")
api.add_resource(AdminGetQueryByQueryId,"/admin/querybyqueryid")
api.add_resource(AdminGetQueryByUserId,"/admin/querybyuserid")
api.add_resource(Unanswered,"/unanswered")

#admin comments
api.add_resource(AdminComment,"/admin/comments")
api.add_resource(AdminGetCommentsByCommentId,"/admin/commentsbycommentid")
api.add_resource(AdminGetCommentsByUserId,"/admin/commentsbyuserid")

#admin users
api.add_resource(AdminLogin,"/admin/login")
api.add_resource(AdminForgotPassword,"/admin/forgotpassword")
api.add_resource(UserDelete,"/admin/userdelete")
api.add_resource(GetProfile,"/admin/getuserprofile")
api.add_resource(GetAllUsers,"/admin/getallusers")

#admin roles
api.add_resource(AdminRoles,"/admin/roles")
api.add_resource(UserRoleUpdate,"/admin/userrolechange")


