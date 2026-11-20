from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import House, Knight, User
from services import spy_service
from repositories.knight_repo import can_see_stats

book_bp = Blueprint("book", __name__)


def person_info(person):
    house = None
    knight = None
    stats = None
    if person.house_id:
        house = db.session.get(House, person.house_id)
    if person.role == "knight":
        knight = db.session.get(Knight, person.id)
    if knight and can_see_stats(current_user, knight):
        stats = knight.get_stats()
    return {"person": person, "house": house, "knight": knight, "stats": stats}

@book_bp.route("/book")
@login_required
def book():
    kind = request.args.get("kind", "knight")
    if kind not in ("knight", "noble"):
        kind = "knight"

    people = User.query.filter_by(role=kind).order_by(User.username).all()

    spread = request.args.get("spread", 0, type=int)
    if spread < 0:
        spread = 0
    first = spread * 2

    left = None
    right = None
    if first < len(people):
        left = person_info(people[first])
    if first + 1 < len(people):
        right = person_info(people[first + 1])

    has_next = first + 2 < len(people)

    gossip = None
    if current_user.role == "knight":
        gossip = spy_service.get_or_create_daily_gossip(current_user.id)
    return render_template("book.html", kind=kind, people=people, left=left, right=right, spread=spread, has_next=has_next, gossip=gossip)


@book_bp.route("/book/reveal/<int:target_id>", methods=["POST"])
@login_required
def reveal_stats(target_id):
    entered_key = request.form.get("gossip_key", "").strip().upper()
    try:
        spy_service.use_gossip_key(current_user, target_id, entered_key)
    except ValueError as error:
        flash(str(error))

    return redirect(url_for("book.book", kind="knight", _anchor=f"person-{target_id}"))