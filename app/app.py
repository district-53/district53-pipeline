import os
from flask import Flask
from config import Config
from extensions import db, login_manager
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)


    @app.cli.command("init-db")
    def init_db():
        import models
        db.create_all()
        print("Tables created")

    @app.cli.command("seed-houses")
    def seed_houses():
        from models import House
        houses = [("Stark", "Winter is coming"), ("Lannister", "Hear me roar"),
                ("Targaryen", "Fire and blood"), ("Baratheon", "Ours is the fury"),
                ("Tyrell", "Growing strong")]
        for name, motto in houses:
            if not House.query.filter_by(name=name).first():
                db.session.add(House(name=name, motto=motto))
        db.session.commit()
        print("Houses ready")

    return app



app = create_app()

if __name__ == "__main__":
    app.run(debug=True)