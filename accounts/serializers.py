from assessments.models import MedicalHealthUser
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

         # Set is_active to False if role is 'counsellor'
        if validated_data.get('role') == 'counsellor':
            validated_data['is_active'] = False
            
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
            'current_post',
            'photo',
        ]

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate_user_id(self, value):
        if not MedicalHealthUser.objects.filter(pk=value, role="Counsellor").exists():
            raise serializers.ValidationError("User is not a counsellor")
        return value
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = MedicalHealthUser.objects.get(pk=user_id)
        profile = CounsellorProfile.objects.create(user=user, **validated_data)
        return profile


class CounsellorProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CounsellorProfile
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'educational_qualifications',
            'years_of_experience_months',
            'current_post',
            'photo',
        ]

