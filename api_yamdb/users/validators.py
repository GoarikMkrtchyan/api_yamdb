from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .constants import USERNAME_REGEX


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError('This username is reserved.')
    return value


def validate_username_format(value):
    validator = RegexValidator(
        regex=USERNAME_REGEX,
        message=(
            'Username can only contain letters,'
            'numbers, hyphens, and underscores.')
    )
    validator(value)
