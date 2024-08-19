from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.utils import timezone
import random
import string


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    ROLES = [
        (USER, 'user'),
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator')
    ]
    username = models.SlugField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    role = models.SlugField(choices=ROLES, default=USER)
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    confirmation_code_expiry = models.DateTimeField(blank=True, null=True)

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
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        self.confirmation_code = code
        self.confirmation_code_expiration = timezone.now() + timezone.timedelta(hours=1)
        self.save()
        return code
