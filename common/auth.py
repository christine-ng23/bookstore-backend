from passlib.hash import bcrypt


def hash_password(raw_password):
    return bcrypt.hash(raw_password)

