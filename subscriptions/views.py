from rest_framework import generics, permissions

from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer


class ActivePlanListView(generics.ListAPIView):
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)


class MySubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.select_related('plan').filter(user=self.request.user)
