from django.db import models

from django.conf import settings


class Notification(models.Model):
    class Kind(models.TextChoices):
        GENERAL = 'general', 'General'
        ACCOUNT = 'account', 'Account'
        MODERATION = 'moderation', 'Moderation'
        SUBSCRIPTION = 'subscription', 'Subscription'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    body = models.TextField()
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.GENERAL)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient}: {self.title}'
