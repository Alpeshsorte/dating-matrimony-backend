from django.db import models


class DashboardSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Dating Admin')
    support_email = models.EmailField(blank=True)
    otp_expiry_minutes = models.PositiveIntegerField(default=10)
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Dashboard settings'
