from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Match
from .serializers import MatchSerializer


class MyMatchListView(generics.ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Match.objects.select_related('requester', 'recipient').filter(
            requester=self.request.user
        ) | Match.objects.select_related('requester', 'recipient').filter(recipient=self.request.user)


class MatchCreateView(generics.CreateAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]


class MatchActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(pk=match_id)
        except Match.DoesNotExist:
            return Response({'detail': 'Match request not found.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action in ('accept', 'reject'):
            if match.recipient != request.user or match.status != Match.Status.PENDING:
                return Response({'detail': 'This action is not allowed.'}, status=status.HTTP_403_FORBIDDEN)
            match.status = Match.Status.ACCEPTED if action == 'accept' else Match.Status.REJECTED
        elif action == 'cancel':
            if match.requester != request.user or match.status != Match.Status.PENDING:
                return Response({'detail': 'This action is not allowed.'}, status=status.HTTP_403_FORBIDDEN)
            match.status = Match.Status.CANCELLED
        else:
            return Response({'detail': 'Action must be accept, reject, or cancel.'}, status=status.HTTP_400_BAD_REQUEST)

        match.save(update_fields=['status', 'updated_at'])
        return Response(MatchSerializer(match).data)
