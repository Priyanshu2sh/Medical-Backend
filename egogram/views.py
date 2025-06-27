from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EgogramTest, Category, EgogramStatement, ResultHistory, User
import random
from collections import defaultdict
from .serializers import EgogramTestSerializer, CategorySerializer, EgogramStatementSerializer, ResultHistorySerializer
from django.db.models import Count

class EgogramTestCreateView(APIView):
    """
    API endpoint to create new EgogramTest instances
    """
    def post(self, request, format=None):
        serializer = EgogramTestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message":"Egogram test created successfully",
                "data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            tests = EgogramTest.objects.all()  # Get all tests
            serializer = EgogramTestSerializer(tests, many=True)
            
            return Response({
                'success': True,
                'count': len(serializer.data),
                'tests': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EgogramTestGetForTest(APIView):
    def get(self, request):
        tests = EgogramTest.objects.annotate(statement_count=Count('statements')).filter(statement_count__gte=20)
        serializer = EgogramTestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryCreateView(APIView):
    """
    API endpoint to create new Category instances
    """
    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            
            return Response({
                'success': True,
                'count': categories.count(),
                'categories': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class EgogramStatementCreateView(APIView):
    """
    API endpoint to create new EgogramStatement instances
    """
    def post(self, request, format=None):
        serializer = EgogramStatementSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Statement created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Invalid data provided',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            statements = EgogramStatement.objects.prefetch_related('category', 'tests').all()
            serializer = EgogramStatementSerializer(statements, many=True)
            
            return Response({
                'success': True,
                'count': statements.count(),
                'statements': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EgogramSTatementUpdateView(APIView):
    def put(self, request, statement_id):
        try:
            statement = EgogramStatement.objects.get(id=statement_id)
        except EgogramStatement.DoesNotExist:
            return Response({
                "message": "Egogram statement not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EgogramStatementSerializer(statement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Egogram statement updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Failed to update egogram statement.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, statement_id):
        try:
            statement = EgogramStatement.objects.get(id=statement_id)
            statement.delete()
            return Response({"message": "Statement deleted successfully."}, status=200)
        except EgogramStatement.DoesNotExist:
            return Response({"message": "Statement not found."}, status=404)

        
class EgogramStatementWithTestView(APIView):
    def get(self, request, test_id):
        try:
            # Ensure the test exists (optional, for better error handling)
            EgogramTest.objects.get(id=test_id)

            # Fetch all statements for the given test
            statements = EgogramStatement.objects.filter(tests__id=test_id)
            serializer = EgogramStatementSerializer(statements, many=True)

            return Response({
                "test_id": test_id,
                "count": len(serializer.data),
                "statements": serializer.data
            }, status=status.HTTP_200_OK)

        except EgogramTest.DoesNotExist:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)
        

#for test only 20 statements with shuffle
class EgogramStatementsWithTestView(APIView):
    def get(self, request, test_id):
        try:
            test = EgogramTest.objects.get(id=test_id)
        except EgogramTest.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch and shuffle statements
        statements = list(test.statements.all())
        random.shuffle(statements)
        selected_statements = statements[:20]

        # Prepare response data
        result = []
        for stmt in selected_statements:
            result.append({
                "id": stmt.id,
                "statement": stmt.statement,
                "test": test.id,
                "test_name": test.test_name
            })

        return Response({
            "test_id": test.id,
            "count": len(result),
            "statements": result
        }, status=status.HTTP_200_OK)


# class EgogramTestCombinedAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = EgogramTestCombinedSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class AddStatementToTestView(APIView):
    """
    POST API to associate a statement with a test (ManyToMany)
    """

    def post(self, request):
        test_id = request.data.get("test_id")
        statement_ids = request.data.get("statement_ids")

        if not test_id or not statement_ids:
            return Response({
                "error": "'test_id' and 'statement_ids' (as a list) are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(statement_ids, list):
            return Response({"error": "'statement_ids' must be a list."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            test = EgogramTest.objects.get(id=test_id)
        except EgogramTest.DoesNotExist:
            return Response({"error": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        valid_statements = EgogramStatement.objects.filter(id__in=statement_ids)

        if not valid_statements:
            return Response({"error": "No valid statement IDs found."}, status=status.HTTP_400_BAD_REQUEST)

        test.statements.add(*valid_statements)

        return Response({
            "message": f"Added {valid_statements.count()} statement(s) to Test {test.id}.",
            "added_statement_ids": [s.id for s in valid_statements]
        }, status=status.HTTP_200_OK)
    


class EgogramResultView(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user")
            statement_marks = request.data.get("statement_marks")

            if not user_id or not statement_marks:
                return Response({"error": "user and statement_marks are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Category-wise score calculation
            category_marks = defaultdict(int)

            for stmt_id_str, mark in statement_marks.items():
                stmt_id = int(stmt_id_str)
                try:
                    stmt = EgogramStatement.objects.select_related('category').get(id=stmt_id)
                    category_id = stmt.category.id
                    # print("statement",stmt)
                    category_marks[category_id] += int(mark)
                except EgogramStatement.DoesNotExist:
                    return Response({"error": f"Statement ID {stmt_id} not found"}, status=status.HTTP_404_NOT_FOUND)

            # Construct final_result text (you can customize this)
            # Find max category
            if category_marks:
                top_category = max(category_marks.items(), key=lambda x: x[1])
                final_result=Category.objects.get(id=top_category[0])
  # Only category_id as string
            else:
                final_result = "0"

            # Save to DB
            result = ResultHistory.objects.create(
                user=user,
                statement_marks=category_marks,
                final_result=final_result
            )

            serializer = ResultHistorySerializer(result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserResultHistoryView(APIView):
    def get(self, request, user_id):
        results = ResultHistory.objects.filter(user_id=user_id).order_by('-created_at')
        if not results.exists():
            return Response({"detail": "No results found for this user."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResultHistorySerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)