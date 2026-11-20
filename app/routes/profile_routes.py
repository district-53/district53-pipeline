from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from extensions import db
from models import House, Knight, Picture, User  # Додано Picture

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


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

        new_username = request.form.get("username", "").strip()
        new_email = request.form.get("email", "").strip()
        new_password = request.form.get("password", "")
        new_role = request.form.get("role", user.role)

        if new_username != user.username and User.query.filter_by(username=new_username).first():
            flash("Цей логін вже зайнятий.")
            return redirect(url_for("profile.view_profile", user_id=user.id))

        if new_email != user.email and User.query.filter_by(email=new_email).first():
            flash("Цей email вже використовується.")
            return redirect(url_for("profile.view_profile", user_id=user.id))

        user.username = new_username
        user.email = new_email

        if new_password:
            user.set_password(new_password)

        # Обробка фото
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            picture = Picture(
                data=photo_file.read(),
                mimetype=photo_file.mimetype,
                filename=photo_file.filename,
            )
            db.session.add(picture)
            db.session.flush()
            user.photo_id = picture.id

        # Оновлення ролі
        if new_role in ("knight", "noble"):
            user.role = new_role

        if user.role in ("knight", "noble"):
            house_id = request.form.get("house_id", type=int)
            user.house_id = house_id

        # Оновлення або створення Knight
        if user.role == "knight":
            if not knight:
                # Перевір models.py: id=user.id або user_id=user.id залежно від назви колонки
                knight = Knight(id=user.id, strength=10, dexterity=10, constitution=10)
                db.session.add(knight)

            knight.strength = request.form.get("strength", type=int, default=knight.strength)
            knight.dexterity = request.form.get("dexterity", type=int, default=knight.dexterity)
            knight.constitution = request.form.get("constitution", type=int, default=knight.constitution)

        db.session.commit()
        flash("Дані користувача успішно збережено!")
        return redirect(url_for("profile.view_profile", user_id=user.id))

    houses = House.query.all()
    return render_template("profile.html", user=user, knight=knight, houses=houses)