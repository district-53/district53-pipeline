from flask import Blueprint, abort, jsonify, redirect, request

import storage

avatar_bp = Blueprint("avatars", __name__, url_prefix="/avatars")


@avatar_bp.route("", methods=["POST"])
def upload_avatar():
    if not storage.is_enabled():
        return jsonify(error="Avatar storage is not configured"), 503

    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify(error="No file in the 'image' field"), 400
    if file.mimetype not in storage.ALLOWED_IMAGE_TYPES:
        return jsonify(error="Only JPG, PNG and WEBP images are allowed"), 400

    key = storage.upload_avatar(file)
    return jsonify(key=key, url=storage.avatar_url(key)), 201


@avatar_bp.route("/<path:key>", methods=["GET"])
def get_avatar(key):
    if not storage.is_enabled():
        abort(503)
    return redirect(storage.avatar_url(key))