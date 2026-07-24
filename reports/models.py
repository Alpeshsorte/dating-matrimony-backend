from django.db import models

from django.conf import settings


class Report(models.Model):
    class Category(models.TextChoices):
        FAKE_PROFILE = 'fake_profile', 'Fake profile'
        SPAM = 'spam', 'Spam'
        HARASSMENT = 'harassment', 'Harassment'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_REVIEW = 'in_review', 'In review'
        RESOLVED = 'resolved', 'Resolved'
        DISMISSED = 'dismissed', 'Dismissed'

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_submitted')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_received')
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_category_display()}: {self.reported_user}'
