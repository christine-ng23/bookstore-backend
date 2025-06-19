def is_equal(dict1, dict2):
    """Compare two dicts"""
    if len(dic1) != len(dic2):
        return False

    for key in dict1:
        if key not in dict2:
            return False
        val1 = dict1[key]
        val2 = dict2[key]
        if isinstance(val1, dict) and isinstance(val2, dict):
            if not is_equal(val1, val2):
                return False
        elif isinstance(val1, dict) and not isinstance(val2, dict):
            if val1 != val2:
                return False
        else:
            return False

    return True
