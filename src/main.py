import os

from db import User

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if len(password) < 8 or password != request.form["confirm"]:
            flash("", "error")
        else:
            user = User(name=name, email=email,
                        password=generate_password_hash(password))
            db.session.add(user)
            try:
                db.session.commit()
                login_user(user)
                return redirect(url_for("dashboard"))
            except IntegrityError:
                db.session.rollback()
                flash("Eлектронна адреса вже зареєстрована.", "error")
        return render_template("register.html", name=name, email=email), 400
    return render_template("register.html")


@app.route("/signup/<role>", methods=["GET", "POST"])
def signup(role):
    if role not in ROLES:
        abort(404)

    if request.method == "POST":
        f = request.form
        username, password = f.get("username", "").strip(), f.get("password", "")
        photo = request.files.get("photo")
        ext = photo.filename.rsplit(".", 1)[-1].lower() if photo and photo.filename else None

        user = User(username=username, role=role,
                    password_hash=generate_password_hash(password))
        error = None
        try:
            if role in ("knight", "noble"):
                user.house = f.get("house", "").strip() or None
            if role == "knight":
                user.strength = int(f["strength"])
                user.agility = int(f["agility"])
                user.endurance = int(f["endurance"])
        except (KeyError, ValueError):
            error = "Strength, agility and endurance must be numbers."

        if not username or len(password) < 8:
            error = "Enter a username and a password of at least 8 characters."
        elif ext and ext not in PHOTO_EXT:
            error = "Photo must be png, jpg, gif or webp."

        if not error:
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error = "This username is taken."

        if error:
            flash(error)
            return render_template("signup.html", role=role), 400

        if ext:
            user.photo = f"{uuid.uuid4().hex}.{ext}"
            photo.save(os.path.join(UPLOAD_DIR, user.photo))
            db.session.commit()
        login_user(user)
        return redirect(url_for("book"))

    return render_template("signup.html", role=role)


@app.route("/book")
@login_required
def book():
    return render_template("book.html")


@app.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)