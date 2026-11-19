from extensions import db
from utils import now

class Picture(db.Model):
    __tablename__ = "pictures"

    id = db.Column(db.Integer, primary_key=True)
    seaweed_fid = db.Column(db.String(255), unique=True, nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    extension = db.Column(db.String(16), nullable=False)
    sha256_hash = db.Column(db.String(64), unique=True, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)