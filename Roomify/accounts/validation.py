def password_validation(password):
    errors = []

# Check length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

# Check lowercase letters
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter (a-z)")

# Check uppercase letters
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter (A-Z)")

# Check numbers
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number (0-9)")

# Check special characters
    specialchars = "!@#$%^&*()+-=[]{};:,.<>/?"
    if not any(c in specialchars for c in password):
        errors.append(f"Password must contain at least one special character")

    return errors