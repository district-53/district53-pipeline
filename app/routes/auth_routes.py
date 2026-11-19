from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import current_user, login_user, login_required, logout_user

from models.user import User, load_user, ROLES
from models.houses import House
from extensions import db
from repositories import user_repo

auth_bp = Blueprint("auth", __name__)


STATS = ("strength", "dexterity", "constitution")
STAT_MIN, STAT_MAX = 1, 100

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('book.book'))
    return render_template("index.html")


@auth_bp.route('/signup', defaults={'role': 'commonfolk'}, methods=['GET', 'POST'])
@auth_bp.route('/signup/<role>', methods=['GET', 'POST'])
def signup(role):
    if current_user.is_authenticated:
        return redirect(url_for('book.book'))

    if role not in ROLES:
        return redirect(url_for('auth.signup', role='commonfolk'))

    houses = House.query.order_by(House.name).all()
    if request.method == "GET":
        return render_template("signup.html", role=role, houses=houses, form={})

    if request.method == 'POST':
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get('password', "")
        
        house_id = None
        if role in ("knight", "noble"):
            house_id = request.form.get("house_id", type=int)

        stats = None
        if role == "knight":
            stats = {name: request.form.get(name, type=int) for name in STATS}
            for name, value in stats.items():
                if value is None or not STAT_MIN <= value <= STAT_MAX:
                    return render_template("signup.html", role=role, houses=houses, form={}), 400

        user = user_repo.create_user(username, email, password, role, house_id=house_id, stats=stats)

    login_user(user)
    return redirect(url_for("book.book"))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('book.book'))

    if request.method == 'POST':
        username = request.form.get('username', "").strip()
        password = request.form.get('password', "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('book.book'))
        flash("Wrong username or password")

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))