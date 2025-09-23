from assessments.models import MedicalHealthUser
from rest_framework import serializers
from .models import CounsellorRequest,TherapySteps, Precaution,Feedback
from accounts.models import CounsellorProfile
class CounsellorProfileSerializer(serializers.ModelSerializer):
    counsellor_id = serializers.IntegerField(source='user.id', read_only=True)
    class Meta:
        model = CounsellorProfile
        fields = [
            'counsellor_id',
            'first_name',
            'last_name',
            'educational_qualifications',
            'years_of_experience_months',
            'current_post',
            'photo',
        ]

class CounsellorListSerializer(serializers.ModelSerializer):
    profile = CounsellorProfileSerializer(source='counsellor_profile')
    
    class Meta:
        model = MedicalHealthUser
        fields = [
            'id',
            'username',
            'email',
            'profile'
        ]
    

class CounsellorRequestSerializer(serializers.ModelSerializer):
    user = CounsellorListSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CounsellorRequest
        fields = ['id', 'user', 'user_id', 'counsellor', 'description', 'created_at', 'status', 'rq_id']
        extra_kwargs = {
            'status': {'read_only': True},
            'user': {'read_only': True},
            'rq_id': {'read_only': True},
        }

    def validate_user_id(self, value):
        if not MedicalHealthUser.objects.filter(pk=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value

    def validate_counsellor(self, value):
        if value.role != 'Counsellor':
            raise serializers.ValidationError("Selected user is not a counsellor.")
        return value

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        return CounsellorRequest.objects.create(user_id=user_id, **validated_data)


class PrecautionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precaution
        fields = ['id', 'description']

class TherapyStepsSerializer(serializers.ModelSerializer):
    precautions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Precaution.objects.all()
    )
    request_id = serializers.PrimaryKeyRelatedField(
        queryset=CounsellorRequest.objects.all(),
        required=True
    )
    

    class Meta:
        model = TherapySteps
        fields = [
            'id','therapy_title', 'trm_id', 'counsellor', 'user','request_id',
            'step_1', 'step_2', 'step_3', 'step_4', 'step_5',
            'step_6', 'step_7', 'step_8', 'step_9', 'step_10',
            'current_step', 'precautions', 'created_at'
        ]
        read_only_fields = ['trm_id', 'created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'therapy_steps', 'user', 'description', 'created_at']