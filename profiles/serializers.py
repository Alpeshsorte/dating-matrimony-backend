from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'is_verified', 'display_name', 'gender', 'date_of_birth',
            'city', 'bio', 'photo', 'is_approved', 'is_hidden', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'username', 'is_verified', 'is_approved', 'is_hidden', 'created_at', 'updated_at']
