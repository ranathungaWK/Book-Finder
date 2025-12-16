from flask import Flask
from database.db_setup import init_db
from routes.auth_routes import auth_bp
from routes.book_identifier_route import book_identifier_bp

def create_app():
    app = Flask(__name__)
    init_db(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(book_identifier_bp, url_prefix='/books')
    return app

app = create_app()

#initialize YOLO model
# device  = "cpu" 
# model = YOLO('models/best.pt').to(device)
# """ if you have a GPU, you can run this code 
#           model = YOLO('models/best.pt')
# """

#initialize easyocr reader
# reader = easyocr.Reader(['en'],gpu=False)



if __name__ == '__main__':
    app.run(debug=True)