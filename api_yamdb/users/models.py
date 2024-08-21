from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint
from django.db import models
from django.utils import timezone
import random
import string


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    ROLES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator')
    ]
    username = models.SlugField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, )
    bio = models.TextField(blank=True)
    role = models.SlugField(choices=ROLES,
                            default=USER)
    first_name = models.CharField('Имя',
                                  max_length=150,
                                  blank=True)
    last_name = models.CharField('Фамилия',
                                 max_length=150,
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
            string.ascii_letters + string.digits, k=6))
        self.confirmation_code = code
        self.confirmation_code_expiration = (
            timezone.now() + timezone.timedelta(hours=1)
        )
        self.save()
        return code
