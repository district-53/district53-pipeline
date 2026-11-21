from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import House, Knight, Picture, User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2 MB


@profile_bp.route("/<int:user_id>", methods=["GET", "POST"])
@login_required
def view_profile(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    knight = db.session.get(Knight, user.id) if user.role == "knight" else None

    if request.method == "POST":
        if current_user.id != user.id:
            abort(403)

        back = redirect(url_for("profile.view_profile", user_id=user.id))

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email:
            flash("Username and email cannot be empty.")
            return back

        if username != user.username and User.query.filter_by(username=username).first():
            flash("This login is already in use.")
            return back

        if email != user.email and User.query.filter_by(email=email).first():
            flash("This email is already in use.")
            return back

        picture = None
        photo = request.files.get("photo")
        if photo and photo.filename:
            data = photo.read()
            if not (photo.mimetype or "").startswith("image/") or len(data) > MAX_PHOTO_SIZE:
                flash("The photo must be an image up to 2 MB.")
                return back
            picture = Picture(data=data, mimetype=photo.mimetype, filename=photo.filename)

        role = user.role
        house_id = user.house_id
        stats = {}

        if user.role in ("knight", "noble"):
            role = request.form.get("role", user.role)
            if role not in ("knight", "noble"):
                flash("Unknown role.")
                return back

            house_id = request.form.get("house_id", type=int)
            if house_id is None or not db.session.get(House, house_id):
                flash("Choose a house.")
                return back

            if role == "knight":
                for name in ("strength", "dexterity", "constitution"):
                    value = request.form.get(name, type=int)
                    if value is None or not 1 <= value <= 100:
                        flash("Stats must be numbers from 1 to 100.")
                        return back
                    stats[name] = value

        user.username = username
        user.email = email
        user.role = role
        user.house_id = house_id

        if password:
            user.set_password(password)

        if picture:
            db.session.add(picture)
            db.session.flush()
            user.photo_id = picture.id

        if role == "knight":
            if knight:
                for name, value in stats.items():
                    setattr(knight, name, value)
            else:
                db.session.add(Knight(id=user.id, **stats))

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("This login or email is already in use.")
            return back

        flash("Users' data updated successfully!")
        return back

    houses = House.query.all()
    return render_template("profile.html", user=user, knight=knight, houses=houses)