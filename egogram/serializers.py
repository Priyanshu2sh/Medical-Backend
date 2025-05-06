from rest_framework import serializers
from .models import EgogramTest, EgogramCategory, EgogramStatement, ResultHistory


class EgogramCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EgogramCategory
        fields = ['id', 'category', 'category_description']
        read_only_fields = ['id']

class EgogramTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EgogramTest
        fields = ['id', 'test_name', 'test_description']
        read_only_fields = ['id']

class EgogramStatementSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category', read_only=True)
    test_name = serializers.CharField(source='test.test_name', read_only=True)
    
    class Meta:
        model = EgogramStatement
        fields = [
            'id', 
            'statement', 
            'category', 
            'category_name',
            'test',
            'test_name'
        ]

    # def to_representation(self, instance):
    #     """Custom representation to show nested category/test details"""
    #     response = super().to_representation(instance)
    #     response['category'] = EgogramCategorySerializer(instance.category).data
    #     response['test'] = EgogramTestSerializer(instance.test).data
    #     return response

    #quiz update

class ResultHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ResultHistory
        fields = [
            'id',
            'user',
            'user_email',
            'statement_marks',
            'final_result',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']