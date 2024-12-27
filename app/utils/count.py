from app.user.models.models import Opinion, Comments
from flask import jsonify
from sqlalchemy import and_
from app import app,db

def update_like_dislike_count(self):  # insert the like and dislike count
    
    likes_dislikes_obj = Opinion.query.filter().all()

    if not likes_dislikes_obj:
        app.logger.info("No comment are liked or disliked ")
        return jsonify(status=404, message="No comment are liked or disliked ")

    for itr in likes_dislikes_obj:
        cmt_like_count = Opinion.query.filter(and_(Opinion.c_id == itr.c_id),
                                                    (Opinion.like == 1)).count()
        cmt_dislike_count = Opinion.query.filter(and_(Opinion.c_id == itr.c_id),
                                                       (Opinion.dislike == 1)).count()

        comment_obj = Comments.query.filter_by(id=itr.c_id).first()
        comment_obj.like_count = cmt_like_count
        comment_obj.dislike_count = cmt_dislike_count
        db.session.commit()

    app.logger.info("Return comments data")
    return jsonify(status=200, message="like and dislike count updated")