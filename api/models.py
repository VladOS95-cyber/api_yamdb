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

    class Meta:
        ordering = ('id', )


class Category(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)


class Title(models.Model):
    name = models.CharField(max_length=300)
    year = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    rating = models.IntegerField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name='Категория'
    )


class Review(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )
