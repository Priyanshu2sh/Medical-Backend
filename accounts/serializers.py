from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, CounsellorProfile  
import random
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'verified_at', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}, 
            'otp': {'read_only': True}, 
            'role': {'required': True}, 
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
    
class CounsellorProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)  # Accept user_id in request
    class Meta:
        model = CounsellorProfile
        fields = [
            'user_id',
            'first_name',
            'middle_name',
            'last_name',
            'educational_qualifications',
            'years_of_experience_months',
            'current_post'
        ]
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate_user_id(self, value):
        if not User.objects.filter(pk=value, role="Counsellor").exists():
            raise serializers.ValidationError("User is not a counsellor")
        return value