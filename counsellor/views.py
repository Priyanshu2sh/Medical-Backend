from assessments.models import MedicalHealthUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CounsellorRequest,TherapySteps,Precaution,Feedback
from .serializers import CounsellorRequestSerializer, CounsellorListSerializer,PrecautionSerializer,TherapyStepsSerializer,FeedbackSerializer
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404


class CreateSessionAPI(APIView):
    permission_classes = []  # No authentication required
    
    def post(self, request):
        serializer = CounsellorRequestSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save()
            return Response({
                "id": session.id,
                "user_id": session.user_id,
                "status": session.status,
                "created_at": session.created_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        sessions = CounsellorRequest.objects.all()
        serializer = CounsellorRequestSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    


class CounsellorListView(APIView):
    def get(self, request):
        counsellors = MedicalHealthUser.objects.filter(role='Counsellor').select_related('counsellor_profile')
        serializer = CounsellorListSerializer(counsellors, many=True)
        return Response(serializer.data)
    
class CounsellorByCounsellorIdView(APIView):
    def get(self, request, counsellor_id):
        try:
            counsellor = MedicalHealthUser.objects.filter(
                role='Counsellor'
            ).select_related('counsellor_profile').get(pk=counsellor_id)
            serializer = CounsellorListSerializer(counsellor)
            return Response(serializer.data)
        except MedicalHealthUser.DoesNotExist:
            raise NotFound("Counsellor not found")
        

class CounsellingRequestsByUserId(APIView):
    def get(self, request, user_id):
        # Optional: validate if the user exists
        if not MedicalHealthUser.objects.filter(id=user_id).exists():
            return Response({'detail': 'MedicalHealthUser not found'}, status=status.HTTP_404_NOT_FOUND)

        sessions = CounsellorRequest.objects.filter(user_id=user_id)
        serializer = CounsellorRequestSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CounsellingRequestsByCounsellorId(APIView):
    def get(self, request, counsellor_id):
        if not MedicalHealthUser.objects.filter(id=counsellor_id, role='Counsellor').exists():
            return Response({'detail': 'Counsellor not found'}, status=status.HTTP_404_NOT_FOUND)

        sessions = CounsellorRequest.objects.filter(counsellor_id=counsellor_id)
        serializer = CounsellorRequestSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateRequestStatusAPI(APIView):
    permission_classes = []  # No authentication required

    def patch(self, request, request_id):
        try:
            session = CounsellorRequest.objects.get(id=request_id)
        except CounsellorRequest.DoesNotExist:
            return Response({"detail": "Counselling request not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.status != 'pending':
            return Response(
                {"detail": f"Status is already '{session.status}'. It cannot be changed."},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Get the new status from the request body
        new_status = request.data.get("status")
        if new_status not in ['accepted', 'rejected']:
            return Response({"detail": "Invalid status. Must be 'accepted' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        session.status = new_status
        session.save()

        return Response({
            "message": f"Status updated to {new_status}.",
            "id": session.id,
            "user_id": session.user_id,
            "counsellor_id": session.counsellor_id,
            "status": session.status
        }, status=status.HTTP_200_OK)
    

class CreatePrecautionAPIView(APIView):
    def post(self, request):
        serializer = PrecautionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        precautions = Precaution.objects.all()
        serializer = PrecautionSerializer(precautions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CreateTherapyStepsAPIView(APIView):
    def post(self, request):
        serializer = TherapyStepsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        therapies = TherapySteps.objects.all()
        serializer = TherapyStepsSerializer(therapies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TherapyStepsByUserView(APIView):
    def get(self, request, user_id):
        therapy_steps = TherapySteps.objects.filter(user_id=user_id)
        if not therapy_steps.exists():
            return Response({"message": "No therapy steps found for this user."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TherapyStepsSerializer(therapy_steps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateCurrentStepAPIView(APIView):
    def patch(self, request, pk):
        try:
            therapy = TherapySteps.objects.get(pk=pk)
        except TherapySteps.DoesNotExist:
            return Response({"error": "Therapy step not found."}, status=status.HTTP_404_NOT_FOUND)

        current_step = request.data.get('current_step')
        if current_step is None:
            return Response({"error": "current_step is required."}, status=status.HTTP_400_BAD_REQUEST)

        therapy.current_step = current_step
        therapy.save()

        return Response({"message": "Current step updated successfully", "current_step": therapy.current_step}, status=status.HTTP_200_OK)
    

class FeedbackCreateView(APIView):
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Feedback submitted successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedbackByCounsellorView(APIView):
    def get(self, request, counsellor_id):
        feedbacks = Feedback.objects.filter(therapy_steps__counsellor__id=counsellor_id)
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response({"feedbacks": serializer.data}, status=status.HTTP_200_OK)