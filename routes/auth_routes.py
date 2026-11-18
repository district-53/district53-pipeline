from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/login")
def login():
    return render_template("login.html")


@auth_bp.route("/signup")
@auth_bp.route("/signup/<role>")
def signup(role="commonfolk"):
    return render_template("signup.html", role=role)