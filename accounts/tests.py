from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationApiTests(APITestCase):
    def test_openapi_schema_is_publicly_available(self):
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('openapi', response.data)
        self.assertIn('/api/auth/register/', response.data['paths'])

    def test_user_can_register_log_in_and_view_current_account(self):
        registration = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'safe-password-123',
            'first_name': 'Alice',
            'last_name': 'Example',
            'phone': '1234567890',
        }

        response = self.client.post('/api/auth/register/', registration, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(username='alice').exists())
        self.assertNotIn('password', response.data)

        response = self.client.post(
            '/api/auth/login/',
            {'username': registration['username'], 'password': registration['password']},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'alice')

# Create your tests here.
