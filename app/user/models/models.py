from enum import unique
from flask_restx.resource import Resource
from app import app,db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    mobile = db.Column(db.String(300), unique=True)
    technology = db.Column(db.String(200))
    password = db.Column(db.String(200))
    roles = db.Column(db.Integer, db.ForeignKey('roles.id'), default=1)
    status=db.Column(db.Boolean,default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    queries = db.relationship('Queries', backref='user_queries')
    comments = db.relationship('Comments', backref='user_comments')
    file=db.relationship('Files',backref='user_files')
    support=db.relationship('Support',backref='support_ticket')


    def __init__(self, name, email, mobile, technology, password,status,created_at, updated_at):
        self.name = name
        self.email = email
        self.mobile = mobile
        self.technology = technology
        self.password = password
        self.status=status
        self.created_at = created_at
        self.updated_at = updated_at


class Technologies(db.Model):
    __tablename__ = "technologies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    queries = db.relationship('Queries', backref='queries_backref')

    def __init__(self, name, created_at, updated_at):
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at


class Queries(db.Model):
    __tablename__ = "queries"
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(300))
    description = db.Column(db.Text)
    t_id = db.Column(db.Integer, db.ForeignKey('technologies.id'))
    filename = db.Column(db.Text)
    filepath = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    status = db.Column(db.Boolean, default=True)
    comments = db.relationship('Comments', backref='comments_on_queries')

    def __init__(self, u_id, title, description, t_id,filename,filepath,created_at, updated_at):
        self.u_id = u_id
        self.title = title
        self.description = description
        self.t_id = t_id
        self.filename=filename
        self.filepath=filepath
        self.created_at = created_at
        self.updated_at = updated_at


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    q_id = db.Column(db.Integer, db.ForeignKey('queries.id'))
    msg = db.Column(db.Text)
    status = db.Column(db.Boolean, default=True)
    filename=db.Column(db.Text)
    filepath=db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    dislike_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    opinion = db.relationship('Opinion', backref='opinion_on_comments')
    file=db.relationship('Files',backref='user_comment_files')

    def __init__(self, u_id, q_id, msg,filename,filepath,created_at,updated_at):
        self.u_id = u_id
        self.q_id = q_id
        self.msg = msg
        self.filename=filename
        self.filepath=filepath
        self.created_at = created_at
        self.updated_at = updated_at



class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status=db.Column(db.Boolean,default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, name, status, created_at, updated_at):
        self.name = name
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        

class Opinion(db.Model):
    __tablename__ = "opinion"
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    c_id= db.Column(db.Integer,db.ForeignKey('comments.id'))
    like = db.Column(db.Boolean, default=0)
    dislike = db.Column(db.Boolean, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, u_id,c_id,like,dislike,created_at, updated_at):
        self.u_id = u_id
        self.c_id = c_id
        self.like=like
        self.dislike=dislike
        self.created_at = created_at
        self.updated_at = updated_at

class Files(db.Model):
    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    path=db.Column(db.String(300))
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    c_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self,name,path,u_id, c_id,created_at, updated_at):
        self.name=name
        self.path=path
        self.u_id = u_id
        self.c_id = c_id
        self.created_at = created_at
        self.updated_at = updated_at

class SavedQueries(db.Model):
    __tablename__ = "saved_queries"
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    q_id = db.Column(db.Integer, db.ForeignKey('queries.id'))
    status = db.Column(db.Boolean,default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self,u_id, q_id, status, created_at, updated_at):
        self.u_id = u_id
        self.q_id = q_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

class Support(db.Model):
    __tablename__ = "support"
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title=db.Column(db.String(300))
    problem=db.Column(db.Text)
    filename = db.Column(db.Text)
    filepath = db.Column(db.Text)
    status=db.Column(db.Boolean,default=True)
    userdelete=db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self,u_id,title,problem,filename,filepath,status,userdelete,created_at,updated_at):
        self.u_id = u_id
        self.title = title
        self.problem=problem
        self.filename=filename
        self.filepath=filepath
        self.status=status
        self.userdelete=userdelete
        self.created_at = created_at
        self.updated_at = updated_at

