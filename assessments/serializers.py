from rest_framework import serializers
from .models import CommonQuestion, CommonTest, StatementOption
# import random

class CommonQuestionSerializer(serializers.ModelSerializer):
    # options = serializers.SerializerMethodField()

    class Meta:
        model = CommonQuestion
        fields = ['id', 'question', 'options']

    # def get_options(self, obj):
    #     options = [
    #         {"category": "logical", "option": obj.logical},
    #         {"category": "analytical", "option": obj.analytical},
    #         {"category": "strategic", "option": obj.strategic},
    #         {"category": "thinking", "option": obj.thinking}
    #     ]
    #     random.shuffle(options)
    #     return options

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
