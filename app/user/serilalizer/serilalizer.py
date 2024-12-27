from app.user.models.models import Technologies,Queries,Opinion,Comments,User,Roles
import ast
from app import app, db


def replace_with_ids(list_of_tech):
    ids_list=[]
    for itr_tech in list_of_tech:
        tech_id=Technologies.query.filter_by(name = itr_tech).first()
        if tech_id:
            ids_list.append(tech_id.id)
    ids_list=f"{ids_list}"
    return ids_list

def string_list_string(technology):
    
    tech_list = []

    technology = ast.literal_eval(technology)

    temp_str = technology[0]
    my_list = list(temp_str.split(", "))

    for itr in my_list:
        tech = Technologies.query.filter_by(name=itr).first()
        tech_id = tech.id
        tech_list.append(tech_id)

    my_string = ','.join([str(x) for x in tech_list])
    return my_string

def user_serializer(user):
    
    technology = ast.literal_eval(str(user.technology))
    tech_list = []

    for itr in technology:
        tech_check = Technologies.query.filter_by(id=int(itr)).first()
        if tech_check:
            tech_list.append(tech_check.name)

    dt = {
        'name': user.name,
        'user_id': user.id,
        'email': user.email,
        'mobile': user.mobile,
        'technology': tech_list,
        'role': db.session.query(Roles).filter_by(id=user.roles).first().name,
        'status':user.status,
        'updated_at':user.updated_at,
    }
    return dt

def query_serializer(query_obj):
    
    dt = {
        'query_id':query_obj.id,
        'user_id':query_obj.u_id,
        'title':query_obj.title,
        'description':query_obj.description,
        'filename':query_obj.filename,
        'filepath':query_obj.filepath,
        'technology_id': db.session.query(Technologies).filter_by(id=query_obj.t_id).first().name,
        'updated_at':query_obj.updated_at
    }

    return dt

def query_comments_serializer(query_obj):
    
    dt = {
        'query_id':query_obj.id,
        'user_id':query_obj.u_id,
        'title':query_obj.title,
        'description':query_obj.description,
        'filename':query_obj.filename,
        'filepath':query_obj.filepath,
        'technology_id': db.session.query(Technologies).filter_by(id=query_obj.t_id).first().name,
        'updated_at':query_obj.updated_at
    }

    comment_objs = db.session.query(Comments).filter_by(q_id=query_obj.id,status=True).all()
    comments_list = []
    for comment in comment_objs:
       data = comment.__dict__
       del data['_sa_instance_state']
       comments_list.append(comment.__dict__)
    dt['comments'] = comments_list
    return dt

def comments_serializer(comments_obj):
    
    query_name = Queries.query.filter_by(id=comments_obj.q_id).first()
    # liked_disliked_or_not = Opinion.query.filter(Opinion.u_id == user_id,
                                                            # Opinion.c_id == comments_obj.id).first()

    dt = {
        'comment_id': comments_obj.id,
        'user_id': comments_obj.u_id,
        'name': (User.query.filter_by(id=comments_obj.u_id).first()).name,
        'query_id': comments_obj.q_id,
        'msg': comments_obj.msg,
        'like_count': comments_obj.like_count,
        'dislike_count': comments_obj.dislike_count,
        'updated_at': comments_obj.updated_at,
        'title': query_name.title,
        'description': query_name.description,
        'status':comments_obj.status
    }

    return dt

def technology_serializer(tech_obj):
    
    dt={
        'tech_id':tech_obj.id,
        'name':tech_obj.name,
        'status':tech_obj.status,
        'updated_at':tech_obj.updated_at
    }
    return dt

def opinion_serializer(opinion_obj):

    dt = {
        'user_id': opinion_obj.u_id,
        'like_status': opinion_obj.like,
        'dislike_status': opinion_obj.dislike,
        'comment_id': opinion_obj.c_id
    }
    try:
        like_dislike_count_find = Comments.query.filter_by(id=opinion_obj.c_id).first()
        dt["comment_like_count"] = like_dislike_count_find.like_count
        dt["comment_dislike_count"] = like_dislike_count_find.dislike_count
    except:
        dt["comment_like_count"] = False
        dt["comment_dislike_count"] = False
    return dt

    # dt={
    #     'u_id':opinion_obj.u_id,
    #     'q_id':opinion_obj.q_id,
    #     'c_id':opinion_obj.c_id
    # }
    # return dt

def admin_serializer(admin):
    dt={
        'name': admin.name,
        'user_id': admin.id,
        'role_id': admin.roles,
        'email_id':admin.email,
        'mobile': admin.mobile
    }
    return dt

def saved_query_serializer(saved_query):

    saved_query_obj = db.session.query(Queries).filter_by(id=saved_query.q_id).first()
   
    dt = {
        'user_id': saved_query.u_id,
        'query_id':saved_query.id,
        'title': saved_query_obj.title,
        'description': saved_query_obj.description,
        'filename': saved_query_obj.filename,
        'filepath': saved_query_obj.filepath
    }

    return dt

def role_serializer(role_obj):

    dt = {
        "role": role_obj.name,
        "created_at": role_obj.created_at,
        "updated_at": role_obj.updated_at,
        "status": role_obj.status
    }

    return dt