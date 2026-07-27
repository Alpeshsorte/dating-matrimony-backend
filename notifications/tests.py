from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Notification


class NotificationApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('alice', password='safe-password-123')
        self.notification = Notification.objects.create(
            recipient=self.user, title='Welcome', body='Thanks for joining.'
        )
        self.client.force_authenticate(self.user)

    def test_user_can_read_and_mark_own_notification(self):
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

        response = self.client.post(f'/api/notifications/{self.notification.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.data['unread_count'], 0)

    def test_user_cannot_mark_another_users_notification_as_read(self):
        other_user = get_user_model().objects.create_user('bob', password='safe-password-123')
        other_notification = Notification.objects.create(recipient=other_user, title='Private', body='For Bob only.')

        response = self.client.post(f'/api/notifications/{other_notification.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Notification.objects.get(pk=other_notification.id).is_read)

# Create your tests here.
