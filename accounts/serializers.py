from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User
import random
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'verified_at', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}, 
            'otp': {'read_only': True}, 
            # 'role': {'read_only': True}, 
            'verified_at': {'read_only': True}
        }
        
    def validate_username(self, value):
        # Allow letters, numbers, spaces, underscores, and dots
        if not re.match(r'^[\w\s.]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, spaces, underscores, and dots."
            )
        return value

    def create(self, validated_data):
        # Hash the password using make_password
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)