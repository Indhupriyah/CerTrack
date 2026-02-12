"""Authentication utilities."""
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string


def hash_password(password):
    return generate_password_hash(password, method="scrypt")


def check_password(password_hash, password):
    return check_password_hash(password_hash, password)


def generate_slug(length=12):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
