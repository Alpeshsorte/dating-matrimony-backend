from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from dating.models import Match
from notifications.models import Notification

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user, is_active=True).prefetch_related('participants')


class StartConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        recipient_id = request.data.get('recipient')
        try:
            recipient = User.objects.get(pk=recipient_id, is_active=True)
        except (User.DoesNotExist, TypeError, ValueError):
            return Response({'detail': 'Active recipient not found.'}, status=status.HTTP_404_NOT_FOUND)

        if recipient == request.user:
            return Response({'detail': 'You cannot start a conversation with yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        accepted_match = Match.objects.filter(
            Q(requester=request.user, recipient=recipient) | Q(requester=recipient, recipient=request.user),
            status=Match.Status.ACCEPTED,
        ).exists()
        if not accepted_match:
            return Response({'detail': 'An accepted match is required to start a conversation.'}, status=status.HTTP_403_FORBIDDEN)

        conversation = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
        created = False
        if conversation is None:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, recipient)
            created = True
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ConversationMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_conversation(self, user, conversation_id):
        return Conversation.objects.filter(pk=conversation_id, participants=user, is_active=True).first()

    def get(self, request, conversation_id):
        conversation = self.get_conversation(request.user, conversation_id)
        if conversation is None:
            return Response({'detail': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)
        messages = conversation.messages.select_related('sender')
        return Response(MessageSerializer(messages, many=True).data)

    def post(self, request, conversation_id):
        conversation = self.get_conversation(request.user, conversation_id)
        if conversation is None:
            return Response({'detail': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(conversation=conversation, sender=request.user)
        conversation.save(update_fields=['updated_at'])
        recipients = conversation.participants.exclude(pk=request.user.pk)
        Notification.objects.bulk_create([
            Notification(
                recipient=recipient,
                title=f'New message from {request.user.username}',
                body=message.content,
            )
            for recipient in recipients
        ])
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
