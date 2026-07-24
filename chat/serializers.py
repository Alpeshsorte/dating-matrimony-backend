from rest_framework import serializers

from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'is_active', 'created_at', 'updated_at']

    def get_participants(self, conversation):
        return [{'id': user.id, 'username': user.username} for user in conversation.participants.all()]


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_username', 'content', 'is_reported', 'created_at']
        read_only_fields = ['id', 'conversation', 'sender', 'sender_username', 'is_reported', 'created_at']
