### book_service/services/user_service.py
"""
User Service Layer

Provides core logic for managing users, including creation, edition, retrieval, and deletion.
This layer focuses solely on input validation, business rules, and persistence.

Responsibilities:
    - Validate input data types for all user-related operations
    - Enforce business rules (e.g., unique usernames, role restrictions)
    - Interact with the data access layer (e.g., database ORM models)
    - Raise appropriate exceptions (ValueError, ForbiddenError) for invalid input or actions
    - Ensure password and sensitive data are securely handled (e.g., hashing)
    - Support reuse by API route layer and internal modules
    - Validation order: input type (-> record existence) -> required/non-empty+format+value (business rule) -> DB checks
    - Uses @validate_types to validate input types and raise ValueError on first error

"""
import re
from typing import Type

from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from book_service.utils.handlers import validate_types
from book_service.utils.utils import validate_required_fields, validate_field_types, filter_valid_model_fields, \
    validate_non_empty_if_present
from common.auth import hash_password
from common.constants import Roles
from common.exceptions import RecordNotFoundError, ForbiddenError
from common.models import User

def valid_username(username, errors):
    """Validate username format: alphanumeric, underscore, dot, hyphen"""
    if not re.match(r'^[a-zA-Z0-9_.-]+$', str(username)):
        errors.append("Username format is invalid. Only letters, numbers, underscores, hyphens, and dots are allowed.")


def valid_user_data(data: dict, is_create: bool):
    """
    Validate user data for required fields and data types, raise ValueError on violations
    :exception: ValueError for all the violations
    """
    errors = []
    # Required or optional-but-present validation
    if is_create:
        required_fields = ["username", "password"]
        validate_required_fields(data, required_fields, errors)
        # Validate username format
        if "username" in data:
            valid_username(data["username"], errors)

        # Field types validation
        validate_field_types(data, {"username": str, "password": str, "role": str}, errors)
    else:
        allowed_to_update_fields = ["password"]
        validate_non_empty_if_present(data, allowed_to_update_fields, errors)
        validate_field_types(data, {"password": str}, errors)

    if errors:
        raise ValueError("; ".join(errors))

def list_users(session: Session) -> list[User]:
    """
    Get all users
    :param session: database session
    :return: list[User]
             list(): if there is no user
    """
    return session.query(User).all()


@validate_types(data=dict, is_admin=bool)
def register_user(session: Session, data: dict, is_admin:bool=False) -> User:
    """
    Create a new user
    :param session: database session
    :param data: dict of user data: {"username": "test", "password": "pw"}
    :param is_admin
    :return: User with password encrypted
    :exception TypeError: function input type error
        ValueError: violations on required fields, field types
            then, invalid role value
        ForbiddenError: insufficient permission action (create user with role "admin")
        ValueError: username is not unique
        IntegrityError: raised by SessionTransaction for constraint violation (e.g., primary_key, unique)
    """
    # Fields validation
    valid_user_data(data, is_create=True)

    # Validate role value
    role = data.get("role", Roles.USER)

    if role not in Roles.ALL:
        raise ValueError(f"Role must be one of: {', '.join(sorted(Roles.ALL))}")

    # Only allow custom role if current user is admin
    if role != Roles.USER and not is_admin:
        raise ForbiddenError("Only admin can assign roles other than 'user'")

    # Filter for valid field names before create model object
    data = filter_valid_model_fields(User, data)
    user = User(**data)
    # Set default role
    if "role" not in data:
        user.role = Roles.USER

    user.password = hash_password(user.password)
    session.add(user)
    try:
        session.commit()
    except IntegrityError as ie:
        session.rollback()
        if "UNIQUE constraint failed" in str(ie.orig):
            raise ValueError("A user with this username already exists.")
        raise
    return user


@validate_types(username=str)
def get_user_by_username(session: Session, username: str) -> User:
    """
    Get user by username
    :param session: database session
    :param username
    :return: User if username is matched
    :exception: TypeError: function input type error
        RecordNotFoundError if username is not matched
    """
    user = session.query(User).filter(User.username == username).first()
    if not user:
        raise RecordNotFoundError(f"User with username {username} not found")
    return user


@validate_types(user_id=int, updates=dict)
def update_user(session: Session, user_id: int, updates: dict) -> User:
    """
    Update a user
    :param session: database session
    :param updates: dict of user update data: {"password": "new pw"}
    :param user_id: user id
    :return: User with password encrypted
    :exception: TypeError: function input type error
        RecordNotFoundError: user_id is not existed
        ValueError: violations on required fields, field types
    """
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise RecordNotFoundError(f"User with id {user_id} not found")

    # Fields validation
    valid_user_data(updates, is_create=False)

    allowed_to_update_fields = ['password']
    for k in allowed_to_update_fields:
        if k in updates:
            setattr(user, k, updates[k])

    if updates.get('password'):
        user.password = bcrypt.hash(user.password)
    session.commit()
    return user


@validate_types(user_id=int)
def delete_user(session: Session, user_id: int) -> User:
    """
    :param session: database session
    :param user_id: user id
    :return: User
    :exception: TypeError: function input type error
        RecordNotFoundError: for non exist user_id
    """
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise RecordNotFoundError(f"User with id {user_id} not found")

    session.delete(user)
    session.commit()
    return user
