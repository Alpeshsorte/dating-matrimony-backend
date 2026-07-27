from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile


class ProfileApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('alice', password='safe-password-123')
        self.client.force_authenticate(self.user)

    def test_user_can_create_and_update_own_profile(self):
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

        response = self.client.patch(
            '/api/profiles/me/',
            {'display_name': 'Alice', 'gender': 'female', 'city': 'Mumbai', 'bio': 'Hello!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Alice')
        self.assertEqual(response.data['city'], 'Mumbai')

# Create your tests here.
