from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models.houses import House
from models.knights import Knight
from models.user import User
from services import spy_service

book_bp = Blueprint("book", __name__)


@book_bp.route("/book")
@login_required
def book():
    rows = (
        db.session.query(Knight, User, House)
        .join(User, Knight.user_id == User.id)
        .outerjoin(House, User.house_id == House.id)
        .order_by(User.id.asc())
        .all()
    )

    total = len(rows)
    total_pages = max(1, (total + 1) // 2)

    page = request.args.get("page", 1, type=int)
    if page < 1 or page > total_pages:
        page = 1

    start = (page - 1) * 2
    current_rows = rows[start : start + 2]

    knights = []
    for knight, user, house in current_rows:
        revealed = spy_service.is_revealed(current_user.id, knight.user_id)
        knights.append({
            "user_id": knight.user_id,
            "username": user.username,
            "knight_type": knight.knight_type,
            "house_name": house.name if house else "No house",
            "is_revealed": revealed,
            "stats": spy_service.show_stats(knight) if revealed else None,
        })

    next_page = page + 1 if page < total_pages else 1

    return render_template(
        "book.html",
        knights=knights,
        page=page,
        total_pages=total_pages,
        next_page=next_page,
        is_knight=(current_user.role == "knight"),
    )


@book_bp.route("/book/gossip-key", methods=["GET"])
@login_required
def get_gossip_key():
    if current_user.role != "knight":
        return jsonify(error="Only knights have gossip keys"), 403

    data = spy_service.get_or_create_daily_gossip(current_user.id)
    return jsonify(
        key=data["key"],
        date=str(data["date"]),
        used_today=data["used_today"],
    )


@book_bp.route("/book/reveal/<int:target_id>", methods=["POST"])
@login_required
def reveal_stats(target_id):
    page = request.form.get("page", 1, type=int)
    entered_key = request.form.get("gossip_key", "").strip()

    try:
        spy_service.use_gossip_key(current_user, target_id, entered_key)
        flash("Stats revealed!")
    except ValueError as e:
        flash(str(e))

    return redirect(url_for("book.book", page=page))