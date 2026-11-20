from extensions import db
from models import House, User
from repositories import user_repo

HOUSES = [
    ("Stark",     "Winter Is Coming"),
    ("Lannister", "Hear Me Roar!"),
    ("Targaryen", "Fire and Blood"),
    ("Baratheon", "Ours Is the Fury"),
    ("Tyrell",    "Growing Strong"),
    ("Mormont",   "Here We Stand"),
    ("Tarth",     ""),
]

KNIGHTS = [
    ("Jaime Lannister", "Lannister", (88, 92, 80), "white"),
    ("Loras Tyrell",    "Tyrell",    (65, 88, 60), "regular"),
    ("Brienne Tarth",   "Tarth",     (90, 70, 85), "regular"),
    ("Jorah Mormont",   "Mormont",   (75, 65, 80), "regular"),
]

NOBLES = [
    ("Ned Stark",        "Stark"),
    ("Cersei Lannister", "Lannister"),
    ("Olenna Tyrell",    "Tyrell"),
]


def add_houses():
    for name, motto in HOUSES:
        if not House.query.filter_by(name=name).first():
            db.session.add(House(name=name, motto=motto))
    db.session.commit()

def add_people():
    for username, house_name, stats, knight_type in KNIGHTS:
        if User.query.filter_by(username=username).first():
            continue
        house = House.query.filter_by(name=house_name).first()
        user_repo.create_user(
            username=username,
            email=username.lower().replace(" ", "_") + "@example.com",
            password=username.split()[-1].lower(),
            role="knight",
            house_id=house.id,
            stats={"strength": stats[0], "dexterity": stats[1], "constitution": stats[2]},
            knight_type=knight_type,
        )

    for username, house_name in NOBLES:
        if User.query.filter_by(username=username).first():
            continue
        house = House.query.filter_by(name=house_name).first()
        user_repo.create_user(
            username=username,
            email=username.lower().replace(" ", "_") + "@example.com",
            password=username.split()[-1].lower(),
            role="noble",
            house_id=house.id,
        )