# from rest_framework import serializers
# from .models import Assessment, Question, Option

# class OptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Option
#         fields = ['id', 'text', 'is_correct']

# class QuestionSerializer(serializers.ModelSerializer):
#     options = OptionSerializer(many=True, read_only=True)

#     class Meta:
#         model = Question
#         fields = ['id', 'text', 'options']

# class AssessmentSerializer(serializers.ModelSerializer):
#     questions = QuestionSerializer(many=True, read_only=True)

#     class Meta:
#         model = Assessment
#         fields = ['id', 'title', 'description', 'questions']
