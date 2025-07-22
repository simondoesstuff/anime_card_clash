def is_float(exp: str) -> bool:
    try:
        float(exp)
        return True
    except ValueError:
        return False