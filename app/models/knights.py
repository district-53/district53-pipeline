from extensions import db
from models.utils import today
from flask import current_app as app

KNIGHT_TYPES = ("regular", "white")

class Knight(db.Model):
    __tablename__ = "knights"
    __table_args__ = (
        db.CheckConstraint("strength BETWEEN 1 AND 100", name="ck_knight_strength"),
        db.CheckConstraint("dexterity BETWEEN 1 AND 100", name="ck_knight_dexterity"),
        db.CheckConstraint("constitution BETWEEN 1 AND 100", name="ck_knight_constitution"),
    )
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    knight_type = db.Column(db.Enum(*KNIGHT_TYPES, name="knight_type"), nullable=False)
    strength = db.Column(db.Integer, nullable=False)
    dexterity = db.Column(db.Integer, nullable=False)
    constitution = db.Column(db.Integer, nullable=False)
    gossip_key = db.Column(db.String(255), unique=True)
    key_date = db.Column(db.Date)

    def set_stats(self, stats: dict):
        if not isinstance(stats, dict):
            raise ValueError("Stats must be a dictionary")

        for name, value in stats.items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"Stat '{name}' must be an integer")
            if not (0 <= value <= 10):
                raise ValueError(f"Stat '{name}' must be between 0 and 10")

        self.stats = stats

    def get_stats(self) -> dict:
        return self.stats or {}
