from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from django.shortcuts import get_object_or_404
from collections import Counter
from django.utils import timezone
from django.utils.timezone import localtime, make_aware, now
from datetime import timedelta

# from rest_framework import status as http_status
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from .models import Hospital, HMSUser, PatientDetails, Findings, PatientFamilyHistory, PatientPastHospitalHistory, MedicalHistoryCurrentHospital, Diseases, OngoingMedication, ClinicalNotes, Medicine, Certificate, Attachments, OPD, PrescriptionItem, Prescription, BillPerticulars, Bill, Invoice, Bed, Ward, DoctorHistory, IPD

from .serializers import HospitalSerializer, HMSUserSerializer, PatientDetailsSerializer, FindingsSerializer, AllergiesSerializer, PatientFamilyHistorySerializer, PatientPastHospitalHistorySerializer, MedicalHistoryCurrentHospitalSerializer, DiseasesSerializer, OngoingMedicationSerializer, MedicineSerializer, ClinicalNotesSerializer, CertificateSerializer, AttachmentsSerializer, OPDSerializer, PrescriptionSerializer, PrescriptionItemSerializer, BillPerticularsSerializer, BillSerializer, InvoiceSerializer, WardSerializer, BedSerializer,IPDSerializer


class HospitalCreateAPIView(APIView):
    def post(self, request):
        # Extract admin user fields from request
        admin_name = request.data.get("admin_name")
        admin_email = request.data.get("admin_email")
        admin_password = request.data.get("admin_password")

        if not all([admin_name, admin_email, admin_password]):
            return Response({
                "error": "Admin name, email, and password are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create hospital
        serializer = HospitalSerializer(data=request.data)
        if serializer.is_valid():
            hospital = serializer.save()
            if not hospital.hospital_id:
                hospital.hospital_id = f"HID{hospital.id:05d}"
                hospital.save(update_fields=['hospital_id'])

            # Create admin user
            hms_user = HMSUser.objects.create(
                name=admin_name,
                email=admin_email,
                password=make_password(admin_password),
                designation='admin',
                hospital=hospital
            )

            hms_user_serializer = HMSUserSerializer(hms_user)

            return Response({
                "message": "Hospital and admin user created successfully.",
                "hospital": serializer.data,
                "admin_data": hms_user_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HMSUserRegisterAPIView(APIView):
    def post(self, request):
        serializer = HMSUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User registered successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HMSUserLoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hms_user = HMSUser.objects.get(email=email)
        except HMSUser.DoesNotExist:
            return Response({"error": "Invalid email or user not found."}, status=status.HTTP_404_NOT_FOUND)

        if not hms_user.is_active:
            return Response({"error": "User account is disabled. Please contact the authorized admin."},
                            status=status.HTTP_403_FORBIDDEN)

        if not check_password(password, hms_user.password):
            return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

        user_data = HMSUserSerializer(hms_user).data

        hospital_data = None
        if hms_user.hospital:
            hospital_data = HospitalSerializer(hms_user.hospital).data
        
        return Response({
            "message": "Login successfully.",
            "hms_user": user_data,
            "hospital": hospital_data  # Full hospital data
        }, status=status.HTTP_200_OK)

        # # If user is not admin, include hospital data
        # if hms_user.designation != "admin" and hms_user.hospital:
        #     from .serializers import HospitalSerializer  # Import only if not already
        #     response_data["hospital"] = HospitalSerializer(hms_user.hospital).data

        # return Response(response_data, status=status.HTTP_200_OK)
    
class GetAllUsersAPIView(APIView):
    def get(self, request):
        hospital_id = request.headers.get('Hospital-Id')  # Make sure frontend sends this in headers

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        users = HMSUser.objects.filter(hospital=hospital).order_by('-id')
        serializer = HMSUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class AdminAddUserAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get('Hospital-ID')  # Use hospital_id from headers
        if not hospital_id:
            return Response({"error": "Hospital ID not provided in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HMSUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hospital=hospital)  # Assign hospital during creation
            return Response({
                "message": "User added successfully",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HMSUserUpdateView(APIView):
    def put(self, request, user_id):
        hospital_id = request.headers.get("Hospital-Id")

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = HMSUser.objects.get(id=user_id, hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"message": "User not found or does not belong to this hospital"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HMSUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HMSUserDeleteView(APIView):
    def delete(self, request, user_id):
        hospital_id = request.headers.get("Hospital-Id")

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = HMSUser.objects.get(id=user_id, hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"message": "User not found or does not belong to this hospital"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        
class HMSUserStatusUpdateView(APIView):
    def patch(self, request, user_id):
        hospital_id = request.headers.get("Hospital-Id")

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = HMSUser.objects.get(id=user_id, hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"message": "User not found or does not belong to this hospital"}, status=status.HTTP_404_NOT_FOUND)

        status_flag = request.data.get("is_active")
        if status_flag is None:
            return Response({"message": "Missing 'is_active' in request body"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = status_flag
        user.save()

        status_text = "enabled" if status_flag else "disabled"
        return Response({"message": f"User {status_text} successfully"}, status=status.HTTP_200_OK)

class AllergiesCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient_id")
        serializer = AllergiesSerializer(data=request.data)

        if serializer.is_valid():
            allergy = serializer.save(hospital=hospital)  # assuming your Allergies model now has a FK to Hospital
            linked_patient = None

            if patient_id:
                try:
                    patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
                    patient.known_allergies.add(allergy)
                    linked_patient = patient_id
                except PatientDetails.DoesNotExist:
                    return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "message": "Allergy created successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data,
                "patient_id": linked_patient
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AllergiesByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        allergies = patient.known_allergies.all()
        serializer = AllergiesSerializer(allergies, many=True)

        return Response({
            "message": "Allergies fetched successfully.",
            "data": {
                "allergies": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }
        }, status=status.HTTP_200_OK)

class PatientDetailsCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientDetailsSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save(hospital=hospital)  # Inject hospital FK
            patient.refresh_from_db()

            return Response({
                'message': 'Patient record created successfully',
                'data': PatientDetailsSerializer(patient).data,
                'hospital': HospitalSerializer(hospital).data  # Include hospital info
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patients = PatientDetails.objects.filter(hospital=hospital, is_active_patient=True).order_by('-date')  # Latest first
        serializer = PatientDetailsSerializer(patients, many=True)
        count = serializer.data

        return Response({
            "patient_count": len(count),
            "patients": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class PatientDetailsUpdateAPIView(APIView):
    def put(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response(
                {"error": "Hospital ID is required in headers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response(
                {"error": "Invalid Hospital ID."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            patient = PatientDetails.objects.get(pk=pk, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response(
                {"error": "Patient not found for this hospital"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PatientDetailsSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Patient record updated successfully",
                "hospital": HospitalSerializer(hospital).data,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response(
                {"error": "Hospital ID is required in headers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response(
                {"error": "Invalid Hospital ID."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            patient = PatientDetails.objects.get(pk=pk, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response(
                {"error": "Patient not found for this hospital"},
                status=status.HTTP_404_NOT_FOUND
            )
        # disable patient
        patient.is_active_patient = False
        patient.save(update_fields=["is_active_patient"])

        return Response(
            {
                "message": "Patient record deleted successfully",
                "hospital": HospitalSerializer(hospital).data
            },
            status=status.HTTP_200_OK
        )

# findings
class FindingsCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['hospital'] = hospital.id

        serializer = FindingsSerializer(data=data)
        if serializer.is_valid():
            finding = serializer.save()
            return Response({
                "message": "Findings record created successfully",
                "hospital": HospitalSerializer(hospital).data,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FindingsByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        findings = Findings.objects.filter(patient_id=patient_id, hospital=hospital)
        if not findings.exists():
            return Response({"message": "No findings found for this patient in this hospital"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FindingsSerializer(findings, many=True)
        return Response({
            "message": "Findings fetched successfully.",
            "hospital": HospitalSerializer(hospital).data,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class FindingsUpdateAPIView(APIView):
    def put(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            finding = Findings.objects.get(pk=pk, hospital=hospital)
        except Findings.DoesNotExist:
            return Response({"error": "Findings record not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FindingsSerializer(finding, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Findings record updated successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_200_OK)     

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PatientFamilyHistoryCreateView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient")
        if not patient_id:
            return Response({"error": "Patient ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientFamilyHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hospital=hospital, patient=patient)
            return Response({
                "message": "Family history record added successfully",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
class PatientFamilyHistoryByPatientView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        records = PatientFamilyHistory.objects.filter(patient=patient)
        if records.exists():
            serializer = PatientFamilyHistorySerializer(records, many=True)
            return Response({
                "message": "Family history records found.",
                "data": {
                    "family_history": serializer.data,
                    "hospital": HospitalSerializer(hospital).data
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "No family history records found for this patient.",
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_404_NOT_FOUND)


class CreatePastHospitalHistoryAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient")
        if not patient_id:
            return Response({"error": "Patient ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientPastHospitalHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hospital=hospital, patient=patient)
            return Response({
                "message": "Past Medical (past Hospital) history added successfully",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPastHospitalHistoryByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        histories = PatientPastHospitalHistory.objects.filter(patient=patient)
        if not histories.exists():
            return Response({"message": "No past history found for this patient"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientPastHospitalHistorySerializer(histories, many=True)
        return Response({
            "message": "Past history (past Hospital) retrieved successfully",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

    
class MedicalHistoryCurrentHospitalCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient")
        if not patient_id:
            return Response({"error": "Patient ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['hospital'] = hospital.id  # Attach hospital FK for saving

        serializer = MedicalHistoryCurrentHospitalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Past medical history (current hospital) added successfully",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class MedicalHistoryCurrentHospitalByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        records = MedicalHistoryCurrentHospital.objects.filter(patient=patient)
        if not records.exists():
            return Response({
                "message": "No history found for this patient."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = MedicalHistoryCurrentHospitalSerializer(records, many=True)
        return Response({
            "message": "Past medical history (current hospital) retrieved successfully",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

    
class DiseasesCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DiseasesSerializer(data=request.data)
        if serializer.is_valid():
            disease = serializer.save(hospital=hospital)
            return Response({
                "message": "Disease record created successfully",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class DiseasesByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        diseases = Diseases.objects.filter(patient=patient, hospital=hospital)
        if not diseases.exists():
            return Response({
                "message": "No diseases found for this patient in this hospital.",
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = DiseasesSerializer(diseases, many=True)
        return Response({
            "message": "Diseases retrieved successfully",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

    
class UpdateDiseaseStatusAPIView(APIView):
    def patch(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            disease = Diseases.objects.get(pk=pk)
        except Diseases.DoesNotExist:
            return Response({"error": "Disease record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if disease's patient is from this hospital
        if disease.patient.hospital != hospital:
            return Response({"error": "This disease record does not belong to the given hospital."}, status=status.HTTP_403_FORBIDDEN)

        # Only allow updating status and/or severity
        status_value = request.data.get('status')
        severity_value = request.data.get('severity')

        if status_value:
            disease.status = status_value
        if severity_value:
            disease.severity = severity_value

        disease.save()

        serializer = DiseasesSerializer(disease)
        return Response({
            "message": "Disease status/severity updated successfully.",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)


class OngoingMedicationCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OngoingMedicationSerializer(data=request.data)
        if serializer.is_valid():
            medication = serializer.save(hospital=hospital)
            return Response({
                "message": "Ongoing medication added successfully",
                "data": OngoingMedicationSerializer(medication).data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OngoingMedicationByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate hospital
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Validate patient within hospital
        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch and serialize medications
        medications = OngoingMedication.objects.filter(patient=patient)
        if not medications.exists():
            return Response({
                "message": "No ongoing medication found for this patient.",
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OngoingMedicationSerializer(medications, many=True)
        return Response({
            "message": "Ongoing medication fetched successfully",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

    
class ClinicalNotesCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClinicalNotesSerializer(data=request.data)
        if serializer.is_valid():
            clinical_note = serializer.save(hospital=hospital)
            return Response({
                "message": "Clinical note added successfully",
                "data": ClinicalNotesSerializer(clinical_note).data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class ClinicalNotesByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        notes = ClinicalNotes.objects.filter(patient=patient, hospital=hospital)
        if notes.exists():
            serializer = ClinicalNotesSerializer(notes, many=True)
            return Response({
                "message": "Clinical notes fetched successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "No clinical notes found for this patient.",
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_404_NOT_FOUND)


class MedicineCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MedicineSerializer(data=request.data, many=True)
        if serializer.is_valid():
            medicine = serializer.save(hospital=hospital)
            return Response({
                "message": "Medicine added successfully",
                "data": MedicineSerializer(medicine, many=True).data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
# class MedicineByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        medicines = Medicine.objects.filter(clinical_note__patient=patient)
        if medicines.exists():
            serializer = MedicineSerializer(medicines, many=True)
            return Response({
                "message": "Medicines fetched successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "No medicines found for this patient.",
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_404_NOT_FOUND)

    
class CertificateCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient")
        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hospital=hospital)
            return Response({
                "message": "Certificate created successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        certificates = Certificate.objects.filter(patient=patient, hospital=hospital)
        serializer = CertificateSerializer(certificates, many=True)
        return Response({
            "message": "Certificates fetched successfully.",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

    

# get all details about a patient in one API
class PatientFullHistoryAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "patient": PatientDetailsSerializer(patient).data,
            "allergies": AllergiesSerializer(patient.known_allergies.all(), many=True).data,
            "family_history": PatientFamilyHistorySerializer(patient.family_history.all(), many=True).data,
            "past_hospital_history": PatientPastHospitalHistorySerializer(patient.past_hospital_history.all(), many=True).data,
            "current_hospital_history": MedicalHistoryCurrentHospitalSerializer(patient.current_hospital_history.all(), many=True).data,
            "diseases": DiseasesSerializer(patient.diseases.all(), many=True).data,
            "ongoing_medications": OngoingMedicationSerializer(patient.ongoing_medications.all(), many=True).data,
        }

        return Response({
            "message": "Patient full history fetched successfully.",
            "hospital": HospitalSerializer(hospital).data,
            "data": data
        }, status=status.HTTP_200_OK)

        
class AttachmentsCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttachmentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hospital=hospital)  # assign hospital explicitly
            return Response({
                "message": "Attachment uploaded successfully",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        attachments = Attachments.objects.filter(patient=patient, hospital=hospital)
        serializer = AttachmentsSerializer(attachments, many=True)

        return Response({
            "message": "Attachments fetched successfully",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)


class OPDCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient")
        doctor_id = request.data.get("doctor")
        description = request.data.get("description")

        if not all([patient_id, doctor_id, description]):
            return Response({"error": "patient, doctor, and description are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        try:
            doctor = HMSUser.objects.get(id=doctor_id, designation='doctor', hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"error": "Doctor not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        # Increment visit count
        patient.visit_count += 1
        patient.save()

        # Create OPD record
        opd = OPD.objects.create(
            hospital=hospital,
            patient=patient,
            doctor=doctor,
            description=description,
            visit_count=patient.visit_count  # set updated count
        )

        serializer = OPDSerializer(opd)
        return Response({
            "message": "OPD entry created successfully.",
            "data": serializer.data,
            "patient": PatientDetailsSerializer(patient).data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        opds = OPD.objects.filter(hospital=hospital).order_by('-date_time')
        serializer = OPDSerializer(opds, many=True)

        # --- ✅ TODAY's STATS CALCULATION ---
        today = timezone.localdate()
        tz = timezone.get_current_timezone()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=tz)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=tz)

        today_opds = opds.filter(date_time__range=(start_of_day, end_of_day))
        total_today = today_opds.count()
        waiting_count = today_opds.filter(status='waiting').count()
        out_count = today_opds.filter(status='out').count()
        completed_count = today_opds.filter(status='completed').count()

        def percent(part):
            return round((part / total_today) * 100, 2) if total_today > 0 else 0

        today_stats = {
           "waiting": waiting_count,
            "out": out_count,
            "completed": completed_count,
            "waiting_percentage": percent(waiting_count),
            "out_percentage": percent(out_count),
            "completed_percentage": percent(completed_count),
        }

        return Response({
            "message": "All OPD records fetched successfully",
            "data": serializer.data,
            "today_stats": today_stats,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)
    
    
class OPDStatusUpdateAPIView(APIView):
    def patch(self, request, opd_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate hospital
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch OPD under this hospital
        try:
            opd = OPD.objects.get(id=opd_id, hospital=hospital)
        except OPD.DoesNotExist:
            return Response({"error": "OPD entry not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)

        # Get and validate new status
        new_status = request.data.get("status")
        valid_statuses = ['waiting', 'active', 'completed', 'out']
        if new_status not in valid_statuses:
            return Response({"error": f"Invalid status. Choose from {valid_statuses}."}, status=status.HTTP_400_BAD_REQUEST)

        opd.status = new_status
        opd.save()

        serializer = OPDSerializer(opd)
        return Response({
            "message": "OPD status updated successfully.",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class OPDListByDoctorAPIView(APIView):
    def get(self, request, doctor_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # All OPDs for doctor
        opds = OPD.objects.filter(doctor_id=doctor_id, hospital=hospital).order_by('-date_time')

        if not opds.exists():
            return Response({"message": "No OPD records found for this doctor in the specified hospital."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Filter OPDs only for today
        # ✅ Get all OPDs for today
         # ✅ Filter OPDs only for today (timezone-aware)
        today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        today_opds = opds.filter(date_time__gte=today_start, date_time__lt=today_end)
        

        total_today = today_opds.count()
        print(f"Total OPDs for today: {total_today}")
        waiting_count = today_opds.filter(status='waiting').count()
        out_count = today_opds.filter(status='out').count()
        completed_count = today_opds.filter(status='completed').count()

        def percent(part):
            return round((part / total_today) * 100, 2) if total_today > 0 else 0


        # ✅ Corrected stats
        today_stats = {
            "waiting_percentage": percent(waiting_count),
            "out_percentage": percent(out_count),
            "completed_percentage": percent(completed_count)
        }


        return Response({
            "message": "OPD records fetched successfully.",
            "data": OPDSerializer(opds, many=True).data,
            "today_stats": today_stats,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)
    

class PrescriptionCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        required_fields = ['patient', 'user', 'items']
        for field in required_fields:
            if field not in data:
                return Response({"error": f"{field} is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=data['patient'], hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        try:
            doctor = HMSUser.objects.get(id=data['user'], designation='doctor', hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"error": "Doctor not found or invalid designation."}, status=status.HTTP_404_NOT_FOUND)

        # Create Prescription
        prescription = Prescription.objects.create(
            patient=patient,
            user=doctor,
            notes=data.get('notes', ''),
            hospital=hospital
        )

        # Create Prescription Items
        for item in data['items']:
            PrescriptionItem.objects.create(
                prescription=prescription,
                medicine_name=item['medicine_name'],
                dosage=item['dosage'],
                duration_days=item['duration_days'],
                instruction=item.get('instruction', '')
            )

        # Serialize
        prescription_data = PrescriptionSerializer(prescription).data
        items_data = PrescriptionItemSerializer(prescription.items.all(), many=True).data

        return Response({
            "message": "Prescription created successfully.",
            "prescription": prescription_data,
            "items": items_data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_201_CREATED)
    

    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        prescriptions = Prescription.objects.filter(hospital=hospital).order_by('-date_issued')
        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response({
            "message": "Prescriptions fetched successfully.",
            "data": serializer.data,
            "hospital": {
                "id": hospital.id,
                "hospital_id": hospital.hospital_id,
                "name": hospital.name,
                "address": hospital.address,
                "owner": hospital.owner,
                "contact": hospital.contact,
            }
        }, status=status.HTTP_200_OK)

class AllMedicineNamesAPIView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        medicines = PrescriptionItem.objects.filter(
            prescription__hospital=hospital
        ).values_list('medicine_name', flat=True).distinct()

        return Response({
            "message": "Medicine names fetched successfully.",
            "hospital": {
                "id": hospital.id,
                "hospital_id": hospital.hospital_id,
                "name": hospital.name,
                "address": hospital.address,
                "owner": hospital.owner,
                "contact": hospital.contact,
            },
            "medicine_names": list(medicines)
        }, status=status.HTTP_200_OK)

class GetPrescriptionsByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        prescriptions = Prescription.objects.filter(patient=patient, hospital=hospital).order_by('-date_issued')

        if not prescriptions.exists():
            return Response({"message": "No prescriptions found for this patient."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response({
            "message": "Prescriptions fetched successfully.",
            "data": serializer.data,
            "hospital": {
                "id": hospital.id,
                "hospital_id": hospital.hospital_id,
                "name": hospital.name,
                "address": hospital.address,
                "owner": hospital.owner,
                "contact": hospital.contact,
            },
        }, status=status.HTTP_200_OK)

class BillperticularsCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['hospital'] = hospital.id

        serializer = BillPerticularsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Bill particular created successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")

        if hospital_id:
            try:
                hospital = Hospital.objects.get(hospital_id=hospital_id)
            except Hospital.DoesNotExist:
                return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

            particulars = BillPerticulars.objects.filter(hospital=hospital, bill__isnull=True)
        else:
            particulars = BillPerticulars.objects.all()

        serializer = BillPerticularsSerializer(particulars, many=True)
        return Response({
            "message": "Bill particulars fetched successfully.",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class BillPerticularsUpdateAPIView(APIView):
    def put(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            particular = BillPerticulars.objects.get(id=pk, hospital=hospital)
        except BillPerticulars.DoesNotExist:
            return Response({"error": "Bill particular not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BillPerticularsSerializer(particular, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Bill particular updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BillPerticularsDeleteAPIView(APIView):
    def delete(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            particular = BillPerticulars.objects.get(id=pk, hospital=hospital)
        except BillPerticulars.DoesNotExist:
            return Response({"error": "Bill particular not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        particular.delete()
        return Response({"message": "Bill particular deleted successfully."}, status=status.HTTP_200_OK)

class BillCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient_id")
        perticulars_data = request.data.get("perticulars")

        if not patient_id or not perticulars_data:
            return Response({"error": "Both patient_id and perticulars are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        # Calculate total amount
        total_amount = sum(item.get("amount", 0) for item in perticulars_data)

        # Create Bill
        bill = Bill.objects.create(
            patient=patient,
            amount=total_amount,
            hospital=hospital,
            status='unpaid'
        )

        # Create Bill perticulars
        for item in perticulars_data:
            BillPerticulars.objects.create(
                name=item['name'],
                amount=item['amount'],
                description=item.get('description'),
                type=item.get('type'),
                bill=bill,
                hospital=hospital
            )

        # Fetch perticulars from DB again (to include auto fields like id/date)
        perticulars = BillPerticulars.objects.filter(bill=bill)

        return Response({
            "message": "Bill created successfully",
            "bill": BillSerializer(bill).data,
            "perticulars": BillPerticularsSerializer(perticulars, many=True).data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_201_CREATED)


    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        bills = Bill.objects.filter(hospital=hospital).order_by('-date')
        serializer = BillSerializer(bills, many=True)

        return Response({
            "hospital": HospitalSerializer(hospital).data,
            "bills": serializer.data
        }, status=status.HTTP_200_OK)

class GetBillsByPatientAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        bills = Bill.objects.filter(patient=patient, hospital=hospital).order_by('-date')

        if not bills.exists():
            return Response({"message": "No bills found for this patient."}, status=status.HTTP_404_NOT_FOUND)

        response_data = []
        for bill in bills:
            perticulars = BillPerticulars.objects.filter(bill=bill)
            response_data.append({
                "bill_id": bill.id,
                "total_amount": bill.amount,
                "status": bill.status,
                "payment_mode": bill.payment_mode,
                "payment_date_time": bill.payment_date_time,
                "paid_amount": bill.paid_amount,
                "date": bill.date,
                "perticulars": BillPerticularsSerializer(perticulars, many=True).data,
                
            })

        return Response({
            "message": "Bills fetched successfully.",
            "data": response_data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class UpdateBillPaymentAPIView(APIView):
    def patch(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            bill = Bill.objects.get(pk=pk, hospital=hospital)
        except Bill.DoesNotExist:
            return Response({"error": "Bill not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)

        if bill.status == 'paid':
            return Response({"error": "This bill is already marked as paid and cannot be changed."},
                            status=status.HTTP_400_BAD_REQUEST)

        payment_mode = request.data.get('payment_mode')
        new_status = request.data.get('status')
        patient_id = request.data.get('patient_id')

        if not payment_mode or new_status != 'paid':
            return Response({"error": "Both payment_mode and status='paid' are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ✅ Get patient
        if not patient_id:
            return Response({"error": "patient_id is required to create invoice."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."},
                            status=status.HTTP_404_NOT_FOUND)

        # ✅ Update bill
        bill.payment_mode = payment_mode
        bill.status = 'paid'
        bill.payment_date_time = timezone.now()
        bill.paid_amount = bill.amount
        bill.save()

        # ✅ Fetch all bill particulars
        perticulars_qs = BillPerticulars.objects.filter(bill=bill)
        perticulars_list = [
            {
                "name": p.name,
                "amount": float(p.amount),
                "description": p.description,
                "type": p.type
            }
            for p in perticulars_qs
        ]

        # ✅ Create Invoice
        invoice = Invoice.objects.create(
            bill=bill,
            patient=patient,
            payment_mode=payment_mode,
            paid_amount=bill.amount,
            particulars=perticulars_list
        )

        return Response({
            "message": "Bill payment updated and invoice generated successfully.",
            "bill_id": bill.id,
            "status": bill.status,
            "payment_mode": bill.payment_mode,
            "payment_date": bill.payment_date_time,
            "paid_amount": bill.paid_amount,
            "invoice": {
                "id": invoice.id,
                "bill": bill.id,
                "patient": {
                    "id": patient.id,
                    "name": patient.full_name,
                    "contact": patient.contact_number
                },
                "paid_amount": invoice.paid_amount,
                "payment_mode": invoice.payment_mode,
                "date": invoice.date,
                "particulars": invoice.particulars
            },
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)
 
# invoice
class InvoiceListAPIView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        invoices = Invoice.objects.filter(bill__hospital=hospital).order_by('-date')
        serializer = InvoiceSerializer(invoices, many=True)

        return Response({
            "message": "All invoices fetched successfully.",
            "hospital": HospitalSerializer(hospital).data,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# IPD starts here
class WardCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WardSerializer(data=request.data)
        if serializer.is_valid():
            ward = serializer.save(hospital=hospital)
            return Response({
                "message": "Ward created successfully",
                "data": WardSerializer(ward).data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllWardsAPIView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        wards = Ward.objects.filter(hospital=hospital).order_by("floor", "ward_name")
        serializer = WardSerializer(wards, many=True)

        return Response({
            "message": "Wards fetched successfully.",
            "hospital": hospital.name,
            "wards": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)
    
class BedCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BedSerializer(data=request.data)
        if serializer.is_valid():
            bed = serializer.save(hospital=hospital)
            return Response({
                "message": "Bed created successfully",
                "data": BedSerializer(bed).data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetBedsByWardAPIView(APIView):
    def get(self, request, ward_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        beds = Bed.objects.filter(ward_id=ward_id, hospital=hospital).order_by('bed_no')
        serializer = BedSerializer(beds, many=True)
        return Response({
            "message": f"Beds for Ward ID {ward_id} fetched successfully.",
            "beds": serializer.data
        }, status=status.HTTP_200_OK)
class WardWithBedsAPIView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        wards = Ward.objects.filter(hospital=hospital).prefetch_related('beds')
        serializer = WardSerializer(wards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateBedStatusAPIView(APIView):
    def patch(self, request, bed_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        bed = get_object_or_404(Bed, id=bed_id, hospital=hospital)

        is_occupied = request.data.get("is_occupied")
        patient_id = request.data.get("patient")

        if is_occupied is True:
            if not patient_id:
                return Response({"error": "Patient ID is required when assigning a bed."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
            except PatientDetails.DoesNotExist:
                return Response({"error": "Patient not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)
            bed.is_occupied = True
            bed.patient = patient
            bed.occupied_date = timezone.now()
            bed.save()

            try:
                ipd = IPD.objects.get(patient=patient, hospital=hospital, bed__isnull=True)
                ipd.bed = bed
                ipd.save(update_fields=["bed"])
            except IPD.DoesNotExist:
                pass  # You can return an error here if you want to ensure bed must map to IPD

        elif is_occupied is False:
            bed.is_occupied = False
            bed.patient = None
            bed.occupied_date = None
            bed.save()

            IPD.objects.filter(bed=bed, hospital=hospital).update(bed=None)


        else:
            return Response({"error": "Invalid value for is_occupied. Must be true or false."}, status=status.HTTP_400_BAD_REQUEST)

        # bed.description = request.data.get("description", bed.description)
        # bed.bed_type = request.data.get("bed_type", bed.bed_type)
        bed.save()

        return Response({
            "message": "Bed status updated successfully.",
            "bed": BedSerializer(bed).data
        }, status=status.HTTP_200_OK)


class IPDCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['hospital'] = hospital.id

        patient_id = data.get('patient')  # because of write_only field
        if patient_id:
            already_admitted = IPD.objects.filter(
                hospital=hospital,
                patient_id=patient_id,
                bed__isnull=False,           # patient is assigned a bed
                transfer_doctor__isnull=True  # patient not yet transferred/discharged
            ).exists()

            if already_admitted:
                return Response({
                    "error": "This patient is already admitted and assigned to a bed."
                }, status=status.HTTP_400_BAD_REQUEST)

        # print("DATA:", data)
        serializer = IPDSerializer(data=data)
        if serializer.is_valid():
            ipd = serializer.save(hospital=hospital)

            # If admitted_doctor is provided, set active_doctor = admitted_doctor
            if ipd.admitted_doctor:
                ipd.active_doctor = ipd.admitted_doctor
                ipd.save(update_fields=['active_doctor'])

            return Response({
                "message": "IPD record created successfully",
                "data": IPDSerializer(ipd).data,
                "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        ipds = IPD.objects.filter(hospital=hospital).select_related(
            'patient', 'admitted_doctor', 'active_doctor', 'transfer_doctor', 'bed'
        ).prefetch_related('doctor_history').order_by('-admit_date')

        serializer = IPDSerializer(ipds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class IPDByDoctorAPIView(APIView):
    def get(self, request, doctor_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            doctor = HMSUser.objects.get(id=doctor_id, designation='doctor')
        except HMSUser.DoesNotExist:
            return Response({"error": "Doctor not found or invalid designation."}, status=status.HTTP_404_NOT_FOUND)

        ipds = IPD.objects.filter(hospital=hospital, active_doctor=doctor).select_related(
            'patient', 'admitted_doctor', 'active_doctor', 'transfer_doctor', 'bed'
        ).prefetch_related('doctor_history').order_by('-admit_date')

        serializer = IPDSerializer(ipds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IPDTransferDoctorAPIView(APIView):
    def patch(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            ipd = IPD.objects.get(pk=pk, hospital=hospital)
        except IPD.DoesNotExist:
            return Response({"error": "IPD not found."}, status=status.HTTP_404_NOT_FOUND)

        transfer_doctor_id = request.data.get("transfer_doctor")
        if not transfer_doctor_id:
            return Response({"error": "transfer_doctor is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_doctor = HMSUser.objects.get(pk=transfer_doctor_id, designation='doctor')
        except HMSUser.DoesNotExist:
            return Response({"error": "Doctor not found or not designated as doctor."}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()

        # Get the latest doctor history to get the from_date
        last_history = DoctorHistory.objects.filter(ipd=ipd, doctor=ipd.active_doctor, till_date__isnull=True).first()

        # Step 1: End current active doctor's history
        if ipd.active_doctor:
            if last_history:
                last_history.till_date = now
                last_history.save()
            else:
                # fallback: if no prior history, assume from_date = ipd.date
                DoctorHistory.objects.create(
                    ipd=ipd,
                    doctor=ipd.active_doctor,
                    from_date=ipd.entry_date,
                    till_date=now,
                    hospital=hospital
                )

        # Step 2: Assign the transfer doctor
        ipd.transfer_doctor = ipd.active_doctor
        ipd.active_doctor = new_doctor
        ipd.save()

        # Step 3: Add new history entry (new doctor)
        DoctorHistory.objects.create(
            ipd=ipd,
            doctor=new_doctor,
            from_date=now,
            till_date=None,
            hospital=hospital
        )

        return Response({
            "message": "Doctor transferred successfully.",
            "ipd_id": ipd.id,
            "new_active_doctor": new_doctor.id,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

        