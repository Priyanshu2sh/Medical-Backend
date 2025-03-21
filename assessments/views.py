from django.shortcuts import render
from rest_framework import status
from accounts.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CommonQuestion, CommonTest
from .serializers import CommonQuestionSerializer, CommonTestSerializer, UserResponseSerializer

    
class CommonQuestionListView(APIView):
    def post(self, request):
        serializer = CommonQuestionSerializer(data=request.data, many=True)  # Allows multiple questions at once

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Questions added successfully",
                "data": serializer.data
                }, 
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request):
        questions = CommonQuestion.objects.all()
        serializer = CommonQuestionSerializer(questions, many=True)
        return Response({"questions": serializer.data})
        # Create your views here.


class ComputeTestResultView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")  # Get user ID from request
        selected_categories = request.data.get("responses")  # Array of category selections

        if not user_id or not selected_categories:
            return Response({"error": "User ID and responses are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Count responses
        category_counts = {
            "logical": selected_categories.count("logical"),
            "analytical": selected_categories.count("analytical"),
            "strategic": selected_categories.count("strategic"),
            "thinking": selected_categories.count("thinking"),
            "skip": selected_categories.count(""),
            "total": len(selected_categories)
        }

        # Save to CommonTest model
        try:
            user = User.objects.get(id=user_id)  # Fetch the user instance
            test_instance = CommonTest.objects.create(
                user_id=user,
                logical=category_counts["logical"],
                analytical=category_counts["analytical"],
                strategic=category_counts["strategic"],
                thinking=category_counts["thinking"],
                skip=category_counts["skip"],
                total=category_counts["total"]
            )
            serializer = CommonTestSerializer(test_instance)
            return Response({"message": "Test results saved successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)