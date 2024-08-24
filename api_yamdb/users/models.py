import random
import string

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .constants import (CONF_CODE_LENGTH, CONF_EXPIRATION_HOURS, EMAIL_LENGTH,
                        MAX_LENGTH)


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    ROLES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator')
    ]
    username = models.SlugField(
        max_length=MAX_LENGTH, unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=('Username can only contain letters,'
                     'numbers, hyphens, and underscores.'),)])
    email = models.EmailField(max_length=EMAIL_LENGTH, )
    bio = models.TextField(blank=True)
    role = models.SlugField(choices=ROLES,
                            default=USER)
    first_name = models.CharField('Имя',
                                  max_length=MAX_LENGTH,
                                  blank=True)
    last_name = models.CharField('Фамилия',
                                 max_length=MAX_LENGTH,
                                 blank=True)
    confirmation_code = models.SlugField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ['id']

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def generate_confirmation_code(self):
        code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=CONF_CODE_LENGTH))
        self.confirmation_code = code
        self.confirmation_code_expiration = (
            timezone.now() + timezone.timedelta(hours=CONF_EXPIRATION_HOURS)
        )
        self.save()
        return code
