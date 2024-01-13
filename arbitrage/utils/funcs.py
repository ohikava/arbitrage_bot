def find_dicts_intersection(dict1: dict, dict2: dict) -> dict:
    """
    Find intersection of dicts
    """
    return set(dict1.keys()) & set(dict2.keys())
    