import random
from django.shortcuts import render
from rest_framework import status
from accounts.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CommonQuestion, CommonTest, StatementOption, QuizName, NewQuiz, QuizResult
from .serializers import CommonQuestionSerializer, CommonTestSerializer, UserResponseSerializer, StatementOptionSerializer, QuizNameSerializer, NewQuizSerializer, QuizResultSerializer
from rest_framework.exceptions import NotFound

class QuizNameView(APIView):
    def get(self, request):
        quiz_names = QuizName.objects.all()
        serializer = QuizNameSerializer(quiz_names, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        serializer = QuizNameSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Quiz category created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewQuizView(APIView):
    # class NewQuizView(APIView):
    # def get(self, request, quiz_id):
    #     new_quizzes = NewQuiz.objects.filter(quiz_id=quiz_id)
    #     serializer = NewQuizSerializer(new_quizzes, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get(self, request, quiz_id):
        new_quizzes = NewQuiz.objects.filter(quiz_id=quiz_id)
        formatted_questions = []

        for question in new_quizzes:
            # Extract options
            options = [
                ("option_1", question.option_1),
                ("option_2", question.option_2),
                ("option_3", question.option_3),
                ("option_4", question.option_4),
            ]

            # Shuffle them
            random.shuffle(options)

            # Turn into a dictionary for the response
            shuffled_options = {key: value for key, value in options}

            # Final response per question
            question_data = {
                "id": question.id,
                "question": question.question,
                **shuffled_options,
                "quiz": {
                    "id": question.quiz.id,
                    "quiz_name": question.quiz.quiz_name,
                    "category_1": question.quiz.category_1,
                    "category_2": question.quiz.category_2,
                    "category_3": question.quiz.category_3,
                    "category_4": question.quiz.category_4
                }
            }
            formatted_questions.append(question_data)

        return Response(formatted_questions, status=status.HTTP_200_OK)
    

    def post(self, request):
        serializer = NewQuizSerializer(data=request.data, many=True)  # Allow multiple quiz questions

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Quiz questions created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, quiz_id, pk=None):
        try:
            quiz_question = NewQuiz.objects.get(pk=pk, quiz_id=quiz_id)
        except NewQuiz.DoesNotExist:
            raise NotFound("Quiz question not found.")

        serializer = NewQuizSerializer(quiz_question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Quiz question updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        try:
            quiz_question = NewQuiz.objects.get(id=id)
            quiz_question.delete()
            return Response({"message": "Quiz question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except NewQuiz.DoesNotExist:
            return Response({"error": "Quiz question not found."}, status=status.HTTP_404_NOT_FOUND)
        
class QuizResultView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        try:
            user = User.objects.get(id=user_id)  # Fetch the User object
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        quiz_id = request.data.get('quiz_id')
        answers = request.data.get('answers', [])  # Format: [{"question_id": 1, "selected_category": "category_1"}, ...]
        
        try:
            quiz = QuizName.objects.get(id=quiz_id)
        except QuizName.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Initialize category counts
        counts = {
            'category_1': 0,
            'category_2': 0,
            'category_3': 0,
            'category_4': 0,
            'skip': 0
        }
        
        for answer in answers:
            selected_category = answer.get('selected_category')
            
            # Validate the category belongs to this quiz
            if selected_category in ['category_1', 'category_2', 'category_3', 'category_4']:
                counts[selected_category] += 1
            else:
                counts['skip'] += 1
        
        # Determine personality result based on highest count
        max_category = max(['category_1', 'category_2', 'category_3', 'category_4'], 
                         key=lambda k: counts[k])
        
        personality_type = getattr(quiz, max_category)  # e.g., "Analytical"
        result = f"{personality_type} Personality" 
        
        # Map to your result types (customize this)
        result_map = {
            'category_1': "Type A Personality",
            'category_2': "Type B Personality",
            'category_3': "Type C Personality",
            'category_4': "Type D Personality",
            'skip': "Undetermined"
        }
        
        # Create QuizResult record
        quiz_result = QuizResult.objects.create(
            user_id=user, 
            quiz=quiz,
            cat_1_marks=counts['category_1'],
            cat_2_marks=counts['category_2'],
            cat_3_marks=counts['category_3'],
            cat_4_marks=counts['category_4'],
            skip=counts['skip'],
            result=result 
        )
        
        serializer = QuizResultSerializer(quiz_result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class QuizResultHistoryView(APIView):
    def get(self, request, user_id):
        try:
            # Fetch quiz results for the user, ordered by latest
            results = QuizResult.objects.filter(user_id=user_id).order_by('-date_taken')
            result_serializer = QuizResultSerializer(results, many=True)

            return Response({
                "quiz_history": result_serializer.data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)



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
        formatted_questions = []

        for question in questions:
            # Extract the category fields and their values
            category_options = [
                ("logical", question.logical),
                ("analytical", question.analytical),
                ("strategic", question.strategic),
                ("thinking", question.thinking),
            ]

            # Shuffle the options
            random.shuffle(category_options)

            # Create a dictionary with shuffled options
            shuffled_options = {key: value for key, value in category_options}

            # Create response data with shuffled options
            question_data = {
                "id": question.id,
                "question": question.question,
                **shuffled_options  # Spread shuffled options into the response
            }

            formatted_questions.append(question_data)

        return Response({"questions": formatted_questions}, status=status.HTTP_200_OK)

    # def get(self, request):
    #     questions = CommonQuestion.objects.all()
    #     serializer = CommonQuestionSerializer(questions, many=True)
    #     return Response({"questions": serializer.data})
    #     # Create your views here.


class ComputeTestResultView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')  # Get user ID from request
        question_type = request.data.get("type")
        selected_categories = request.data.get("responses")  # Array of category selections

        if not user_id or not selected_categories:
            return Response(
                {"error": "User ID and responses are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
         # Validate type field
        if question_type not in ["mcq", "statement-based"]:
            return Response(
                {"error": "Invalid question type. Allowed types: 'mcq', 'statement-based'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Count responses for each category
        category_counts = {
            "logical": selected_categories.count("logical"),
            "analytical": selected_categories.count("analytical"),
            "strategic": selected_categories.count("strategic"),
            "thinking": selected_categories.count("thinking"),
            "skip": selected_categories.count(""),
            "total": len(selected_categories)
            
        }

        total = category_counts["total"]
        # non_skip_total = total - category_counts["skip"]

        if total:
            # Calculate percentage 
            logical_pct = round((category_counts["logical"] / total) * 100, 2)
            analytical_pct = round((category_counts["analytical"] / total) * 100, 2)
            strategic_pct = round((category_counts["strategic"] / total) * 100, 2)
            thinking_pct = round((category_counts["thinking"] / total) * 100, 2)
            skip_pct = round((category_counts["skip"] / total) * 100, 2)

            percentages = {
                "logical_percentage": f"{logical_pct}%",
                "analytical_percentage": f"{analytical_pct}%",
                "strategic_percentage": f"{strategic_pct}%",
                "thinking_percentage": f"{thinking_pct}%",
                "skip_percentage": f"{skip_pct}%"
            }

            category_counts.pop("skip")  
            category_counts.pop("total") 
            maximum_category = max(category_counts, key=category_counts.get)

            # Calculate average 
            average_count = round(
                (category_counts["logical"] +
                 category_counts["analytical"] +
                 category_counts["strategic"] +
                 category_counts["thinking"]) / 4, 2
            )

            # Calculate average percentage 
            average_percentage = round((logical_pct + analytical_pct + strategic_pct + thinking_pct) / 4, 2)
        else:
            percentages = {
                "logical_percentage": "0%",
                "analytical_percentage": "0%",
                "strategic_percentage": "0%",
                "thinking_percentage": "0%",
                "skip_percentage": "0%"
            }
            average_count = 0
            average_percentage = 0
            maximum_category = None

        # Save the computed results to CommonTest model
        try:
            user = User.objects.get(id=user_id) 
            test_instance = CommonTest.objects.create(
                user_id=user,
                logical=category_counts["logical"],
                analytical=category_counts["analytical"],
                strategic=category_counts["strategic"],
                thinking=category_counts["thinking"],
                skip=request.data.get("responses").count(""),
                total=request.data.get("responses").count(""),
                result = maximum_category,
                type=question_type
            )
            serializer = CommonTestSerializer(test_instance)
           
            return Response({
                "message": "Test results saved successfully",
                "type": question_type,
                "data": serializer.data,
                "statistics": percentages,
                "average_count": average_count,
                "average_percentage": f"{average_percentage}%",
            }, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class StatementOptionView(APIView):
    def post(self, request):
        serializer = StatementOptionSerializer(data=request.data, many=isinstance(request.data, list))
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Statement options added successfully",
                "data": serializer.data
                }, 
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        options = StatementOption.objects.all()
        # formatted_options = []

        # for option in options:
        #     # Create a dictionary of available options
        #     all_options = {
        #         "logical": option.logical,
        #         "analytical": option.analytical,
        #         "strategic": option.strategic,
        #         "thinking": option.thinking
        #     }

        #     # Randomly select 2 keys
        #     selected_keys = random.sample(list(all_options.keys()), 2)

        #     # Create a dictionary with only the selected keys
        #     selected_options = {key: all_options[key] for key in selected_keys}

        #     formatted_options.append(selected_options)

        # return Response({"options": formatted_options}, status=status.HTTP_200_OK)
        serializer = StatementOptionSerializer(options, many=True)
        return Response({"options": serializer.data})
    

class TestHistoryView(APIView):
    def get(self, request, user_id):
        try:
            # Fetch all test records for the given user
            test_history = CommonTest.objects.filter(user_id=user_id).order_by("-created_at")
            test_serializer = CommonTestSerializer(test_history, many=True)

            # Fetch all statement options (if needed)
            statement_options = StatementOption.objects.all()
            statement_serializer = StatementOptionSerializer(statement_options, many=True)

            return Response({
                "test_history": test_serializer.data,
                "statement_options": statement_serializer.data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
