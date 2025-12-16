import re 

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def is_valid_email(email: str) -> bool:
    """Validate the given email address."""

    return bool(re.match(EMAIL_REGEX, email))

def is_strong_password(password: str) -> bool:
    """Check if the password is strong enough."""

    return (len(password) >= 8)

def is_valid_username(username: str) -> bool:
    """validate the given username."""

    return 3 <= len(username) <= 30