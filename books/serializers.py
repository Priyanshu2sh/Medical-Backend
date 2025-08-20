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



class DashboardStatsSerializer(serializers.Serializer):
    books_count = serializers.IntegerField()
    codes_count = serializers.IntegerField()
    total_users_count = serializers.IntegerField()
    counsellors_count = serializers.IntegerField()