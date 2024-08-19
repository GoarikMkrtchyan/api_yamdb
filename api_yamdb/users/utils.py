from django.core.mail import send_mail
from django.conf import settings


def send_confirmation_code(user):
    code = user.generate_confirmation_code()
    send_mail(
        'Your confirmation code',
        f'Your confirmation code is {code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
