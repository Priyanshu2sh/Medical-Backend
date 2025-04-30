from rest_framework import serializers
from .models import CommonQuestion, CommonTest, StatementOption, QuizName, NewQuiz, QuizResult, McqQuiz, McqQuestions, McqQuizResult

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
    category_scores = serializers.SerializerMethodField()

    class Meta:
        model = QuizResult
        fields = [
            'id',
            'user_id',
            'quiz',
            'quiz_name',
            'category_scores',  # Replaces cat_1_marks to cat_4_marks
            'skip',
            'result',
            'date_taken'
        ]

    def get_category_scores(self, obj):
        return {
            obj.quiz.category_1: obj.cat_1_marks,
            obj.quiz.category_2: obj.cat_2_marks,
            obj.quiz.category_3: obj.cat_3_marks,
            obj.quiz.category_4: obj.cat_4_marks,
        }

class McqQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = McqQuestions
        fields = '__all__'
        # fields = ['id', 'quiz', 'question', 'options_1', 'options_2', 'options_3', 'options_4', 'correct_ans', 'type']


class McqQuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = McqQuiz
        fields = ['id', 'type', 'name', 'description','question']

    def create(self, validated_data):
        questions = validated_data.pop('questions', [])
        quiz = McqQuiz.objects.create(**validated_data)
        return quiz
    

class McqQuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = McqQuizResult
        fields = '__all__'  # or list fields manually if you want