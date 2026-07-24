from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import Profile
from .serializers import ProfileSerializer


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class PublicProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(is_approved=True, is_hidden=False, user__is_active=True)
