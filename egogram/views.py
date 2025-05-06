from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EgogramTest, EgogramCategory, EgogramStatement
from .serializers import EgogramTestSerializer, EgogramCategorySerializer, EgogramStatementSerializer

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
    

class EgogramCategoryCreateView(APIView):
    """
    API endpoint to create new EgogramCategory instances
    """
    def post(self, request, format=None):
        serializer = EgogramCategorySerializer(data=request.data)
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
            categories = EgogramCategory.objects.all()
            serializer = EgogramCategorySerializer(categories, many=True)
            
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
        serializer = EgogramStatementSerializer(data=request.data)
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
            statements = EgogramStatement.objects.select_related('category', 'test').all()
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
        
class EgogramStatementWithTestView(APIView):
    def get(self, request):
        try:
            test_id = request.query_params.get('test_id')  # Read ?test_id=<id>
            statements = EgogramStatement.objects.select_related('category', 'test')

            if test_id:
                statements = statements.filter(test__id=test_id)

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