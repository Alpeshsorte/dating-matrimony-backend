from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Match

User = get_user_model()


class MatchSerializer(serializers.ModelSerializer):
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = Match
        fields = ['id', 'requester', 'requester_username', 'recipient', 'recipient_username', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'requester', 'requester_username', 'recipient_username', 'status', 'created_at', 'updated_at']

    def validate_recipient(self, recipient):
        requester = self.context['request'].user
        if recipient == requester:
            raise serializers.ValidationError('You cannot send a match request to yourself.')
        if Match.objects.filter(requester=requester, recipient=recipient).exists() or Match.objects.filter(requester=recipient, recipient=requester).exists():
            raise serializers.ValidationError('A match request already exists between these users.')
        return recipient

    def create(self, validated_data):
        return Match.objects.create(requester=self.context['request'].user, **validated_data)
