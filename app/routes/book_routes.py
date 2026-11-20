from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import House, Knight, User
from services import spy_service

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
            
    gossip = None
    if current_user.role == "knight":
        gossip = spy_service.get_or_create_daily_gossip(current_user.id)

    return render_template("book.html", kind=kind, people=people, person=person,
                           house=house, knight=knight, stats=stats, gossip=gossip)


@book_bp.route("/book/reveal/<int:target_id>", methods=["POST"])
@login_required
def reveal_stats(target_id):
    entered_key = request.form.get("gossip_key", "").strip().upper()
    try:
        spy_service.use_gossip_key(current_user, target_id, entered_key)
    except ValueError as error:
        flash(str(error))

    return redirect(url_for("book.book", kind="knight", id=target_id))