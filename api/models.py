from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    USER_ROLES = [
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    ]

    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        unique=True
    )
    role = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True
    )
    bio = models.TextField(blank=True)

    def is_admin(self):
        return self.role == 'admin' or self.is_staff

    def is_moderator(self):
        return self.role == 'moderator'
