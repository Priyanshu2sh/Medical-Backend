from rest_framework import serializers
from .models import CommonQuestion, CommonTest, StatementOption, QuizName, NewQuiz, QuizResult, McqQuiz, McqQuestions

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


class QuizResultSerializer(serializers.ModelSerializer):
    quiz_name = serializers.CharField(source='quiz.quiz_name')  # Fetch quiz name from the QuizName model

    class Meta:
        model = QuizResult
        fields = ['id', 'user_id', 'quiz', 'quiz_name', 'cat_1_marks', 'cat_2_marks', 'cat_3_marks', 'cat_4_marks', 'skip', 'result', 'date_taken']


class McqQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = McqQuestions
        fields = '__all__'


class McqQuizSerializer(serializers.ModelSerializer):
    # Accept a list of question IDs for assigning to the quiz
    questions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=McqQuestions.objects.all()
    )

    class Meta:
        model = McqQuiz
        fields = ['id', 'type', 'name', 'description', 'questions']

    def create(self, validated_data):
        questions = validated_data.pop('questions', [])
        quiz = McqQuiz.objects.create(**validated_data)
        quiz.questions.set(questions)  # Set the M2M relationship
        return quiz