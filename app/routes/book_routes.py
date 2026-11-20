from flask import Blueprint, render_template, request
from flask_login import login_required

from extensions import db
from models import House, Knight, User

book_bp = Blueprint("book", __name__)


@book_bp.route("/book")
@login_required
def book():
    kind = request.args.get("kind", "knight")
    if kind not in ("knight", "noble"):
        kind = "knight"

    people = User.query.filter_by(role=kind).order_by(User.username).all()

    selected_id = request.args.get("id", type=int)
    person = next((p for p in people if p.id == selected_id), people[0] if people else None)

    house = None
    knight = None
    stats = None
    if person:
        if person.house_id:
            house = db.session.get(House, person.house_id)
        if person.role == "knight":
            knight = db.session.get(Knight, person.id)

    return render_template("book.html", kind=kind, people=people, person=person, house=house, knight=knight, stats=stats)
