from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50,
        choices=(
            ('user', 'User'),
            ('moderator', 'Moderator'),
            ('admin', 'Admin'),
        ),
        default='user',
    )
    confirmation_code = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'
