from django.core.exceptions import ValidationError
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail


def send_confirmation_code(user):
    if user.confirmation_code and user.confirmation_code_expiration > timezone.now():
        raise ValidationError("Confirmation code already sent and not expired.")

    confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    user.confirmation_code = confirmation_code
    user.confirmation_code_expiration = timezone.now() + timedelta(minutes=10)
    user.save()

    send_mail(
        'Your confirmation code',
        f'Your confirmation code is {confirmation_code}',
        'noreply@yourdomain.com',
        [user.email],
        fail_silently=False,
    )
