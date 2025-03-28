from rest_framework import serializers
from .models import Books, Descriptions, CodeReaction

class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__'

class DescriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptions
        fields = '__all__'
        
class CodeReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeReaction
        fields = '__all__'
