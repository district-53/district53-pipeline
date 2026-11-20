from extensions import db

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

    def set_stats(self, strength, dexterity, constitution):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution

    def get_stats(self) -> dict:
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
        }
