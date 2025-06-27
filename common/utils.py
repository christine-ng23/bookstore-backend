def assert_json_structure(response_json, expected_structure):
    """
    Recursively checks whether response_json contains expected_structure.
    expected_structure should be a dict with keys (and optionally types or substructures).
    """
    assert isinstance(response_json, dict), f"Expected dict, got {type(response_json)}"

    for key, expected_type in expected_structure.items():
        assert key in response_json, f"Missing key: '{key}'"
        if isinstance(expected_type, type):
            assert isinstance(response_json[key], expected_type), f"Expected '{key}' to be {expected_type}, got {type(response_json[key])}"
        elif isinstance(expected_type, list):
            assert isinstance(response_json[key], list), f"Expected '{key}' to be a list"
            if expected_type and isinstance(expected_type[0], type) and response_json[key]:
                for item in response_json[key]:
                    assert isinstance(item, expected_type[0]), f"Expected list item in '{key}' to be {expected_type[0]}, got {type(item)}"
        elif isinstance(expected_type, dict):
            assert_json_structure(response_json[key], expected_type)
