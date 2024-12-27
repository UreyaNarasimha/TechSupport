from app import app,db


if __name__ == "__main__":
    with app.app_context():
       db.create_all()
    app.run(host='0.0.0.0',port=5001, debug=True)
    # app.run(host='0.0.0.0',port=5001, debug=True,ssl_context=context)
    # app.run(host="192.168.5.225",debug=True)
