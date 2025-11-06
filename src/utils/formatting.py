import re

def snake_case(text):
    # Gère les séquences de majuscules/chiffres comme un seul mot
    s1 = re.sub(r'(?<=[a-z])(?=[A-Z0-9])|(?<=[A-Z0-9])(?=[A-Z][a-z])', '_', text)
    return s1.lower()