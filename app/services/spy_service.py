import secrets
from extensions import db
from models.knights import Knight
from models.spy import Spy
from models.user import User
from models.utils import today
import hashlib
import random
import string
from models.utils import now
from repositories.user_repo import update


def generate_gossip_key(user_id: int) -> str:
    while True:
        current_time = now()
        mixed_number = user_id * int(current_time.timestamp())
        letters_list = random.choices(string.ascii_uppercase, k=4)
        random_letters = "".join(letters_list)
        raw_string = f"{mixed_number}-{random_letters}"
        raw_bytes = raw_string.encode("utf-8")
        hash_object = hashlib.sha256(raw_bytes)
        digest = hash_object.hexdigest()

        short_hash = digest[:8].upper()
        key = f"GOSP-{short_hash}"

        exists = Knight.query.filter_by(gossip_key=key).first()
        if not exists:
            return key


def has_used_today(knight_id: int) -> bool:
    reveal = Spy.query.filter_by(viewer_id=knight_id, reveal_date=today()).first()
    return reveal is not None


def is_revealed(viewer_id: int, target_id: int) -> bool:
    if viewer_id == target_id:
        return True
    reveal = Spy.query.filter_by(viewer_id=viewer_id, target_id=target_id).first()
    return reveal is not None


def get_or_create_daily_gossip(knight_id: int) -> dict:
    knight = db.session.get(Knight, knight_id)
    current_date = today()

    if knight.key_date != current_date or not knight.gossip_key:
        new_key = generate_gossip_key(knight_id)
        update(knight, gossip_key=new_key, key_date=current_date)

    return {
        "key": knight.gossip_key,
        "date": knight.key_date,
        "used_today": has_used_today(knight_id),
    }


def show_stats(target_knight: Knight) -> dict:
    return target_knight.get_stats()


def use_gossip_key(viewer: User, target_entered_id: int, entered_key: str) -> dict:
    if viewer.role != "knight" or not viewer.knight:
        raise ValueError("Only knights can use gossip keys")

    if viewer.id == target_entered_id:
        raise ValueError("You already know your own stats")

    target_knight = db.session.get(Knight, target_entered_id)
    if not target_knight:
        raise ValueError("Target knight not found")

    if is_revealed(viewer.id, target_entered_id):
        return show_stats(target_knight)

    if has_used_today(viewer.id):
        raise ValueError("You have already used your gossip key today")

    if viewer.knight.key_date != today() or not viewer.knight.gossip_key:
        raise ValueError("Your gossip key has expired, refresh the page")

    if entered_key != viewer.knight.gossip_key:
        raise ValueError("Invalid gossip key")

    reveal = Spy(
        viewer_id=viewer.id,
        target_id=target_entered_id,
        reveal_date=today(),
    )
    db.session.add(reveal)
    db.session.commit()

    return show_stats(target_knight)