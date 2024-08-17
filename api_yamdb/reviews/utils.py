from django.core.mail import send_mail


def send_confirmation_email(user):
    subject = 'Your confirmation code'
    message = f'Your confirmation code: {user.confirmation_code}'
    send_mail(subject, message, 'from@example.com', [user.email])
