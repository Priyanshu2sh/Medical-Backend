from rest_framework import serializers
from .models import CounsellorRequest

class CounsellorRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounsellorRequest
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},      # Auto-set from logged-in user
            'status': {'read_only': True}     # Defaults to 'pending'
        }

    def validate_counsellor(self, value):
        """Ensure selected user is actually a counsellor"""
        if value.role != 'Counsellor':
            raise serializers.ValidationError("Selected user is not a counsellor")
        return value