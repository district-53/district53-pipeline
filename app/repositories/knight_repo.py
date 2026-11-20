from extensions import db
from models import Knight, Spy
from models.utils import today


def get_knight(user_id):
    return db.session.get(Knight, user_id)


def has_active_reveal(viewer_id, target_id):
    return db.session.query(Spy.id).filter_by(
        viewer_id=viewer_id, target_id=target_id, reveal_date=today()
    ).first() is not None


def can_see_stats(viewer, knight):
    if viewer.role == "noble":
        return True
    if viewer.id == knight.user_id:
        return True
    if knight.knight_type == "white":
        return True
    if viewer.role == "knight":
        return has_active_reveal(viewer.id, knight.user_id)
    return False
