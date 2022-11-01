from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    u_id = models.CharField(unique=True, max_length=50, null=True)
    username = models.CharField(unique=True, max_length=50, null=True)
    chat_id = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return f'{self.username}'

    class Meta:
        ordering = ['id']
