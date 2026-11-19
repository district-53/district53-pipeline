import uuid
import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

ALLOWED_IMAGE_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}

_s3 = None
_bucket = None


def init_storage(app):
    global _s3, _bucket
    if not app.config.get("S3_ENDPOINT"):
        app.logger.warning("S3_ENDPOINT is not set: avatar upload is disabled")
        return

    _bucket = app.config["S3_BUCKET"]
    _s3 = boto3.client(
        "s3",
        endpoint_url=app.config["S3_ENDPOINT"],
        aws_access_key_id=app.config["S3_ACCESS_KEY"],
        aws_secret_access_key=app.config["S3_SECRET_KEY"],
        region_name="us-east-1",
        config=BotoConfig(s3={"addressing_style": "path"}),
    )

    try:
        _s3.head_bucket(Bucket=_bucket)
    except ClientError:
        try:
            _s3.create_bucket(Bucket=_bucket)
        except ClientError as e:
            if e.response["Error"]["Code"] not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                raise


def is_enabled():
    return _s3 is not None


def upload_avatar(file, user_id):
    extension = ALLOWED_IMAGE_TYPES[file.mimetype]
    folder = f"users/{user_id}" if user_id else "uploads"
    key = f"{folder}/{uuid.uuid4()}.{extension}"
    _s3.upload_fileobj(file, _bucket, key, ExtraArgs={"ContentType": file.mimetype})
    return key


def avatar_url(key, expires_in=3600):
    return _s3.generate_presigned_url(
        "get_object", Params={"Bucket": _bucket, "Key": key}, ExpiresIn=expires_in
    )


def delete_object(key):
    _s3.delete_object(Bucket=_bucket, Key=key)