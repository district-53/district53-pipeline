from flask import Flask
from config import Config
from extensions import db
from storage import init_storage
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.avatar_routes import avatar_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    init_storage(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(avatar_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)