from rest_framework import serializers
from .models import Books, Descriptions

class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__'

class DescriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptions
        fields = '__all__'
