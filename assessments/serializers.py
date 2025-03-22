from rest_framework import serializers
from .models import CommonQuestion, CommonTest, StatementOption


class CommonQuestionSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = CommonQuestion
        fields = '__all__'


class CommonTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonTest
        fields = '__all__'

class UserResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    responses = serializers.ListField(
        child=serializers.DictField()  # Each response contains question_id and selected_option
    )

class StatementOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementOption
        fields = '__all__'
