import hashlib 
from flask import Blueprint, Response, abort, jsonify, redirect, request, url_for
from flask_login import current_user, login_required
import storage
from extensions import db
from models.picture import Picture
from models.user import User

picture_bp = Blueprint("pictures", __name__)


@picture_bp.route("/me/avatar", methods=["POST"])
@login_required
def upload_my_avatar():
    if not storage.is_enabled():
        return jsonify(error="Picture storage is not configured"), 503

    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify(error="No file in the 'image' field"), 400
    if file.mimetype not in storage.ALLOWED_IMAGE_TYPES:
        return jsonify(error="Only JPG, PNG and WEBP images are allowed"), 400

    data = file.read()
    sha256 = hashlib.sha256(data).hexdigest()

    picture = Picture.query.filter_by(sha256_hash=sha256).first()
    if picture is None:
        extension = storage.ALLOWED_IMAGE_TYPES[file.mimetype]
        key = f"pictures/{sha256}.{extension}"
        storage.upload_bytes(data, key, file.mimetype)

        picture = Picture(
            seaweed_fid=key,
            size_bytes=len(data),
            extension=extension,
            sha256_hash=sha256,
            uploaded_by=current_user.id,
        )
        db.session.add(picture)
        db.session.flush()

    current_user.photo_id = picture.id
    db.session.commit()

    return jsonify(
        picture_id=picture.id,
        url=url_for("pictures.get_picture", picture_id=picture.id),
    ), 201


@picture_bp.route("/pictures/<int:picture_id>", methods=["GET"])
def get_picture(picture_id):
    picture = db.session.get(Picture, picture_id)
    if picture is None:
        abort(404)

    data, content_type = storage.download(picture.seaweed_fid)
    return Response(data, mimetype=content_type,
                    headers={"Cache-Control": "public, max-age=31536000, immutable"})


@picture_bp.route("/users/<int:user_id>/avatar", methods=["GET"])
def get_user_avatar(user_id):
    user = db.session.get(User, user_id)
    if user is None or user.photo_id is None:
        abort(404)
    return redirect(url_for("pictures.get_picture", picture_id=user.photo_id))