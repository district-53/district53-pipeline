from extensions import db

class House(db.Model):
    __tablename__ = "houses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    motto = db.Column(db.Text, nullable=False)
    sigil_id = db.Column(db.Integer, db.ForeignKey("pictures.id"))