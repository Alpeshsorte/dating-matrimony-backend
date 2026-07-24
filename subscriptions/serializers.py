from rest_framework import serializers

from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'price', 'duration_days']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'status', 'starts_at', 'ends_at', 'created_at']
