from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User
import random

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'verified_at']
        extra_kwargs = {'password': {'write_only': True}, 'otp': {'read_only': True}, 'role': {'read_only': True}, 'verified_at': {'read_only': True}}

    def create(self, validated_data):
        # Hash the password using make_password
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)