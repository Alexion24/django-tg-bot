from __future__ import annotations
from django.db import models

from users.models import User


class TgUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    u_id = models.CharField(unique=True, max_length=50, null=True)
    username = models.CharField(max_length=150, null=True)
    chat_id = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.username}' if self.username is not None else f'{self.user}'

    class Meta:
        ordering = ['user']


class WebhookMessage(models.Model):
    received_at = models.DateTimeField(auto_now_add=True, help_text="When we received the event.")
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["received_at"]),
        ]
