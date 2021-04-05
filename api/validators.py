from datetime import datetime

from django.core.exceptions import ValidationError


def custom_year_validator(value):
    if value > datetime.now().year:
        raise ValidationError(
            ('Year cant be greater then current.'),
            params={'value': value},
        )
