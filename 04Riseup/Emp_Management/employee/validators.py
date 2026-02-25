from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# -----------------------
# Validators
# -----------------------


def validate_appcube_email(value: str) -> None:
    """Ensure email starts with 'appcubeemployee' (case-insensitive) as requirement."""
    try:
        validate_email(value)
    except ValidationError:
        raise
    if not value.lower().startswith("appcubeemployee"):
        raise ValidationError("Email must start with 'appcubeemployee'")
