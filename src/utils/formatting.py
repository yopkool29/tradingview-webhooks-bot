import re


def snake_case(text):
    # Gère les séquences de majuscules/chiffres comme un seul mot
    s1 = re.sub(r"(?<=[a-z])(?=[A-Z0-9])|(?<=[A-Z0-9])(?=[A-Z][a-z])", "_", text)
    return s1.lower()


def _convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        logger.error(f"Failed to convert {value} to float")
        return None


def _convert_to_int(value):
    try:
        return int(value)
    except ValueError:
        logger.error(f"Failed to convert {value} to int")
        return None
