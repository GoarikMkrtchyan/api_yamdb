from datetime import datetime

from django.core.exceptions import ValidationError


def validate_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(
            f"Год выпуска не может быть больше текущего ({current_year}).")
