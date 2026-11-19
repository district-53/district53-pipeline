import json
from extensions import db
from utils import today
from flask import current_app as app

KNIGHT_TYPES = ("regular", "white")

class Knight(db.Model):
    __tablename__ = "knights"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    knight_type = db.Column(db.Enum(*KNIGHT_TYPES), name="knight_type", nullable=False)
    stats = db.Column(db.Text, nullable=False)
    gossip_key = db.Column(db.String(255), unique=True)
    key_date = db.Column(db.Date)

    def set_stats(self, strength, dexterity, constitution):
        self.stats = json.dumps({"strength": strength, "dexterity": dexterity, "constitution": constitution})

    def get_stats(self):
        return json.loads(self.stats)
