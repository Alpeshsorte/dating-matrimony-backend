from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Report

User = get_user_model()


class ReportSerializer(serializers.ModelSerializer):
    reported_username = serializers.CharField(source='reported_user.username', read_only=True)
    reported_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))

    class Meta:
        model = Report
        fields = ['id', 'reported_user', 'reported_username', 'category', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reported_username', 'status', 'created_at', 'updated_at']

    def validate_reported_user(self, reported_user):
        if reported_user == self.context['request'].user:
            raise serializers.ValidationError('You cannot report yourself.')
        return reported_user

    def create(self, validated_data):
        return Report.objects.create(reporter=self.context['request'].user, **validated_data)
