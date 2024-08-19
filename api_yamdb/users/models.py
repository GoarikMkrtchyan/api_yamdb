from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.utils import timezone
from datetime import timedelta


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

    # # Добавил, чтобы в сериализаторе поля автор был не айди, а имя
    # def __str__(self):
    #     return (self.username)
