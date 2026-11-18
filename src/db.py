import os
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://myuser:mypassword@localhost:5432/mydb",   #не промахай додати сюди дані підключення БД, блеать!!!!!!!!!!!!!!!!!!!!!!!!!!!!
)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    roles = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()