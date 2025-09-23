from rest_framework import serializers
from egogram.models import Category
from .models import CommonQuestion, CommonTest, MedicalHealthUser, StatementOption, QuizName, NewQuiz, QuizResult, McqQuiz, McqQuestions, McqQuizResult, Steps, Treatment, Feedback

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    role = serializers.CharField(required=True)

    class Meta:
        model = MedicalHealthUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password', "role"]

    def create(self, validated_data):
        user = MedicalHealthUser(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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

    # for create the opbejt on egogram category also 
    def create(self, validated_data):
        # Create QuizName object first
        quiz = QuizName.objects.create(**validated_data)

        # Create or update categories in egogram.Category table
        for cat_field in ['category_1', 'category_2', 'category_3', 'category_4']:
            cat_name = validated_data.get(cat_field)
            if cat_name:
                Category.objects.get_or_create(
                    category=cat_name,
                    defaults={'category_description':quiz.quiz_description}
                )

        return quiz


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
    questions = McqQuestionsSerializer(many=True, required=False)

    class Meta:
        model = McqQuiz
        fields = ['id', 'type', 'name', 'description', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = McqQuiz.objects.create(**validated_data)

        for question_data in questions_data:
            McqQuestions.objects.create(quiz=quiz, **question_data)
        return quiz

class McqQuizSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = McqQuiz
        fields = ['id', 'type', 'name', 'description']


class McqQuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = McqQuizResult
        fields = '__all__'  # or list fields manually if you want

class StepsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Steps
        fields = [
            'id',
            'type',
            'category',
            'category_name',
            'step_1', 'step_2', 'step_3', 'step_4', 'step_5',
            'step_6', 'step_7', 'step_8', 'step_9', 'step_10'
        ]
        
        


class TreatmentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Treatment
        fields = [
            'id', 'category', 'category_name', 'user', 'steps',
            'type', 'current_step', 'created_at'
        ]

class FeedbackSerializer(serializers.ModelSerializer):
    step_data = serializers.SerializerMethodField()
    class Meta:
        model = Feedback
        fields = '__all__'

    def validate_description(self, value):
        if "steps" not in value or "note" not in value:
            raise serializers.ValidationError("`description` must contain 'steps' and 'note' keys.")
        return value
    
    def get_step_data(self, obj):
        """
        Optionally include step content if description['steps'] refers to a Steps.id.
        """
        step_ref = obj.description.get('steps')
        if isinstance(step_ref, int):  # If it's an ID reference
            try:
                step_obj = Steps.objects.get(id=step_ref)
                # Return all steps or one step; here returning all for reference
                return {
                    "step_1": step_obj.step_1,
                    "step_2": step_obj.step_2,
                    "step_3": step_obj.step_3,
                    "step_4": step_obj.step_4,
                    "step_5": step_obj.step_5,
                    "step_6": step_obj.step_6,
                    "step_7": step_obj.step_7,
                    "step_8": step_obj.step_8,
                    "step_9": step_obj.step_9,
                    "step_10": step_obj.step_10,
                }
            except Steps.DoesNotExist:
                return {"error": "Step reference not found"}
        return step_ref  # Return actual JSON if not ID