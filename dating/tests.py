from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Match
from notifications.models import Notification


class MatchApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.alice = user_model.objects.create_user('alice', password='safe-password-123')
        self.bob = user_model.objects.create_user('bob', password='safe-password-123')

    def test_recipient_can_accept_a_match_request(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post('/api/matches/request/', {'recipient': self.bob.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        match_id = response.data['id']
        self.assertTrue(Notification.objects.filter(recipient=self.bob, title='New match request').exists())

        self.client.force_authenticate(self.bob)
        response = self.client.post(f'/api/matches/{match_id}/action/', {'action': 'accept'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], Match.Status.ACCEPTED)

        self.assertEqual(Match.objects.get(pk=match_id).status, Match.Status.ACCEPTED)
        self.assertTrue(Notification.objects.filter(recipient=self.alice, title='Match request accepted').exists())

    def test_user_cannot_request_a_match_with_themself(self):
        self.client.force_authenticate(self.alice)
        response = self.client.post('/api/matches/request/', {'recipient': self.alice.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_recipient_can_accept_a_match_request(self):
        match = Match.objects.create(requester=self.alice, recipient=self.bob)
        self.client.force_authenticate(self.alice)

        response = self.client.post(f'/api/matches/{match.id}/action/', {'action': 'accept'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Match.objects.get(pk=match.id).status, Match.Status.PENDING)

    def test_invalid_match_action_is_rejected(self):
        match = Match.objects.create(requester=self.alice, recipient=self.bob)
        self.client.force_authenticate(self.bob)

        response = self.client.post(f'/api/matches/{match.id}/action/', {'action': 'archive'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# Create your tests here.
