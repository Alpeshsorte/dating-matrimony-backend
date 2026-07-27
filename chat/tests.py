from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from dating.models import Match
from notifications.models import Notification


class ChatApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.alice = user_model.objects.create_user('alice', password='safe-password-123')
        self.bob = user_model.objects.create_user('bob', password='safe-password-123')

    def test_accepted_match_can_start_a_conversation_and_send_a_message(self):
        Match.objects.create(requester=self.alice, recipient=self.bob, status=Match.Status.ACCEPTED)
        self.client.force_authenticate(self.alice)

        response = self.client.post('/api/chats/start/', {'recipient': self.bob.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation_id = response.data['id']

        response = self.client.post(
            f'/api/chats/{conversation_id}/messages/', {'content': 'Hi Bob!'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hi Bob!')
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.bob,
                title='New message from alice',
                body='Hi Bob!',
            ).exists()
        )

    def test_chat_requires_an_accepted_match(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post('/api/chats/start/', {'recipient': self.bob.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_participant_cannot_read_conversation_messages(self):
        charlie = get_user_model().objects.create_user('charlie', password='safe-password-123')
        Match.objects.create(requester=self.alice, recipient=self.bob, status=Match.Status.ACCEPTED)
        self.client.force_authenticate(self.alice)
        conversation_id = self.client.post('/api/chats/start/', {'recipient': self.bob.id}, format='json').data['id']

        self.client.force_authenticate(charlie)
        response = self.client.get(f'/api/chats/{conversation_id}/messages/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# Create your tests here.
