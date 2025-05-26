from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CounsellorRequest
from .serializers import CounsellorRequestSerializer

class CreateSessionAPI(APIView):
    permission_classes = []  # No authentication required
    
    def post(self, request):
        serializer = CounsellorRequestSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save()
            return Response({
                "id": session.id,
                "status": session.status,
                "created_at": session.created_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)