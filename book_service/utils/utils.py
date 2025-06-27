## book_service/utils/utils.py
from sqlalchemy.orm import class_mapper

def is_empty(value):
    return value is None or (not value and value != 0)

def validate_required_fields(data: dict, required_fields: list, errors: list):
    """Validate the required fields are in data dict"""
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

def validate_non_empty_if_present(data: dict, fields: list, errors):
    """Validate the value of fields if the field is in data dict"""
    for field in fields:
        if field in data and is_empty(data[field]):
            errors.append(f"Missing required field: {field}")

def validate_field_types(data: dict, expected_types: dict, errors: list):
    """Validate the type of fields if the field is in data dict"""
    for field, expected_type in expected_types.items():
        if field in data and not isinstance(data[field], expected_type):
            expected = expected_type.__name__ if isinstance(expected_type, type) else " or ".join(t.__name__ for t in expected_type)
            errors.append(f"Field '{field}' must be of type {expected}")

def validate_non_negative_fields(data: dict, fields: list, errors: list):
    """Validate the value of fields non-negative if the field is in data dict"""
    for field in fields:
        if field in data and data[field] < 0:
            errors.append(f"Field '{field}' must be non-negative")


def filter_valid_model_fields(model_class, data: dict) -> dict:
    """Filter data to allow only fields that are model_class attributes"""
    valid_keys = {prop.key for prop in class_mapper(model_class).iterate_properties}
    return {k: v for k, v in data.items() if k in valid_keys and k!="id"}

