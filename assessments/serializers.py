from rest_framework import serializers
from .models import CommonQuestion, CommonTest, StatementOption, QuizName, NewQuiz

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


class QuizNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizName
        fields = '__all__'


class NewQuizSerializer(serializers.ModelSerializer):
    quiz = QuizNameSerializer(read_only=True)  # Nested serializer for read
    quiz_id = serializers.PrimaryKeyRelatedField(
        queryset=QuizName.objects.all(), source='quiz', write_only=True
    )  # For write

    class Meta:
        model = NewQuiz
        fields = ['id', 'question', 'option_1', 'option_2', 'option_3', 'option_4', 'quiz', 'quiz_id']