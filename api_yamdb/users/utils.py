import random
import string

from django.core.mail import send_mail

from api_yamdb.settings import DEFAULT_FROM_EMAIL

from .constants import CONF_CODE_LENGTH


def send_confirmation_code(user):
    confirmation_code = ''.join(random.choices(
        string.ascii_letters + string.digits, k=CONF_CODE_LENGTH))
    user.confirmation_code = confirmation_code
    user.save()

    send_mail(
        'Your confirmation code',
        f'Your confirmation code is {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
