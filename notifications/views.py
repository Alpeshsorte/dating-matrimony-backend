from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class UnreadNotificationCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'unread_count': Notification.objects.filter(recipient=request.user, is_read=False).count()})


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        updated = Notification.objects.filter(pk=notification_id, recipient=request.user, is_read=False).update(is_read=True)
        if not updated and not Notification.objects.filter(pk=notification_id, recipient=request.user).exists():
            return Response({'detail': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'Notification marked as read.'})
