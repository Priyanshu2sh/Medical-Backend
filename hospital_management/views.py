from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status as http_status
from collections import Counter
from django.utils import timezone
from django.utils.timezone import localtime, make_aware, now
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from datetime import timedelta
from django.db import transaction
import random, jwt, os
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal

# from rest_framework import status as http_status
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from .models import Hospital, HMSUser, PatientDetails, Findings, PatientFamilyHistory, PatientPastHospitalHistory, MedicalHistoryCurrentHospital, Diseases, OngoingMedication, ClinicalNotes, Medicine, Certificate, Attachments, OPD, PrescriptionItem, Prescription, BillPerticulars, Bill, Invoice, Bed, Ward, DoctorHistory, IPD, Supplier, PharmacyBill, PharmacyMedicine, StockTransaction, MedicineStock, PatientAppointment, DoctorTimetable, LabReport, BirthRecord, DeathReport, DoctorProfile, PharmacyOutBill, InvoicePharmacyBill, PharmacyOutInvoice

from .serializers import HospitalSerializer, HMSUserSerializer, PatientDetailsSerializer, FindingsSerializer, AllergiesSerializer, PatientFamilyHistorySerializer, PatientPastHospitalHistorySerializer, MedicalHistoryCurrentHospitalSerializer, DiseasesSerializer, OngoingMedicationSerializer, MedicineSerializer, ClinicalNotesSerializer, CertificateSerializer, AttachmentsSerializer, OPDSerializer, PrescriptionSerializer, PrescriptionItemSerializer, BillPerticularsSerializer, BillSerializer, InvoiceSerializer, WardSerializer, BedSerializer,IPDSerializer, SupplierSerializer, PharmacyBillSerializer, PharmacyMedicineSerializer, MedicineStockSerializer, StockTransactionSerializer, PatientRegisterSerializer, PatientAppointmentSerializer, AppointmentStatusUpdateSerializer, PatientAppointmentResponseSerializer, DoctorTimetableSerializer, LabReportSerializer, BirthRecordSerializer, DeathReportSerializer, DoctorProfileSerializer, PharmacyOutBillSerializer, InvoicePharmacyBillSerializer, PharmacyOutInvoiceSerializer


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

class GetHospitalByIdView(APIView):
    def get(self, request, hospital_id):
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Hospital not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HospitalSerializer(hospital)
        return Response({
            "message": "Hospital fetched successfully",
            "hospital": serializer.data
        }, status=status.HTTP_200_OK)

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

class AvailableDoctorsView(APIView):
    def get(self, request):
        hospital_id = request.headers.get('Hospital-Id')  # Make sure frontend sends this in headers

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Get doctors with is_doctor_available = True for this hospital
        available_doctors = HMSUser.objects.filter(
            hospital=hospital,
            designation='doctor',
            is_doctor_available=True
        )

        data = []
        for doctor in available_doctors:
            # Get doctor's profile (if exists)
            try:
                doctor_profile = DoctorProfile.objects.get(doctor=doctor, hospital=hospital)
                doctor_profile_data = DoctorProfileSerializer(doctor_profile).data
            except DoctorProfile.DoesNotExist:
                doctor_profile_data = None

            # Combine HMSUser data with DoctorProfile data
            doctor_data = HMSUserSerializer(doctor).data
            doctor_data["doctor_profile"] = doctor_profile_data

            data.append(doctor_data)

        return Response({
            "hospital": HospitalSerializer(hospital).data,
            "available_doctors": data
        }, status=status.HTTP_200_OK)


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

class DoctorProfileCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        doctor_id = request.data.get("doctor")
        if not doctor_id:
            return Response({"error": "Doctor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = HMSUser.objects.get(id=doctor_id, hospital=hospital, designation="doctor")
        except HMSUser.DoesNotExist:
            return Response({"error": "Doctor not found for this hospital or invalid designation."}, status=status.HTTP_404_NOT_FOUND)

        if DoctorProfile.objects.filter(doctor=doctor, hospital=hospital).exists():
            return Response({"error": "Doctor profile already exists for this hospital."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DoctorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor, hospital=hospital)
            return Response({
                "message": "Doctor profile created successfully.", 
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
                }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorProfileUpdateAPIView(APIView):
    def patch(self, request, doctor_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            doctor_profile = DoctorProfile.objects.get(doctor_id=doctor_id, hospital=hospital)
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Doctor profile not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorProfileSerializer(doctor_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(hospital=hospital)
            return Response({
                "message": "Doctor profile updated successfully.", 
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorProfileDetailAPIView(APIView):
    def get(self, request, doctor_id):
        # Get Hospital ID from headers
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            doctor_profile = DoctorProfile.objects.get(doctor_id=doctor_id, hospital=hospital)
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Doctor profile not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorProfileSerializer(doctor_profile)
        return Response({
            "message": "Doctor profile fetched successfully.",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

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

class UpdateDoctorAvailabilityView(APIView):
    def patch(self, request, *args, **kwargs):
        hospital_id = request.headers.get("Hospital-Id")
        doctor_id = kwargs.get("doctor_id")
        is_available = request.data.get("is_doctor_available")

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)
        

        if is_available is None:
            return Response({"error": "Missing 'is_doctor_available' in request body."}, status=400)

        doctor = get_object_or_404(HMSUser, id=doctor_id, designation="doctor")

        doctor.is_doctor_available = is_available
        doctor.save()

        return Response({
            "message": "Doctor availability status updated successfully.",
            "doctor_id": doctor.id,
            "is_doctor_available": doctor.is_doctor_available,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class GetHMSUserWithHospitalView(APIView):
    def get(self, request, user_id):
        hospital_id = request.headers.get("Hospital-Id")

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=400)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=404)

        try:
            hms_user = HMSUser.objects.get(id=user_id, hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"error": "HMS User not found for this hospital."}, status=404)

        response_data = {
            "hospital": HospitalSerializer(hospital).data,
            "hms_user": HMSUserSerializer(hms_user).data
        }

        if hms_user.designation.lower() == "doctor":
            try:
                doctor_profile = DoctorProfile.objects.get(doctor=hms_user, hospital=hospital)
                response_data["doctor_profile"] = DoctorProfileSerializer(doctor_profile).data
            except DoctorProfile.DoesNotExist:
                response_data["doctor_profile"] = None  

        return Response(response_data, status=200)


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

class GetPatientDetailsByIdView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            patient = PatientDetails.objects.get(hospital=hospital, id=patient_id)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PatientDetailsSerializer(patient)
        return Response({
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
            }, status=status.HTTP_200_OK)

class PatientRegisterView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        hospital_id = data.get('hospital_id')

        if not hospital_id:
            return Response({"error": "Hospital ID is required in body"}, status=400)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            patient = PatientDetails.objects.get(email=email, hospital__hospital_id=hospital_id)
            if patient.email_otp and not patient.verified_at:
                patient.email_otp = random.randint(100000, 999999)
                patient.save()
                send_mail(
                    "OTP Verification",
                    f"Your OTP is {patient.email_otp}",
                    os.getenv('EMAIL_HOST_USER'),
                    [patient.email],
                )
                return Response({"message": "OTP resent", "patient_id": patient.id}, status=200)
            return Response({"error": "Email already verified"}, status=400)
        except PatientDetails.DoesNotExist:
            data['hospital'] = hospital.id
            data['password'] = make_password(data.get('password'))
            serializer = PatientDetailsSerializer(data=data)
            if serializer.is_valid():
                patient = serializer.save()
                otp = random.randint(100000, 999999)
                patient.email_otp = otp
                patient.save()
                send_mail(
                    "OTP Verification",
                    f"Your One-Time Password (OTP) for completing your registration is: {otp}",
                    os.getenv('EMAIL_HOST_USER'),
                    [patient.email],
                )
                return Response({"message": "OTP sent", "patient_id": patient.id}, status=201)
            return Response(serializer.errors, status=400)

class VerifyPatientOTPView(APIView):
    def post(self, request):
        patient_id = request.data.get("patient_id")
        email_otp = request.data.get("email_otp")

        try:
            patient = PatientDetails.objects.get(id=patient_id, email_otp=email_otp, verified_at__isnull=True)
            patient.verified_at = now()
            patient.email_otp = None
            patient.save()
            return Response({"message": "OTP verified successfully"}, status=200)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Invalid OTP or already verified"}, status=400)


class PatientLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response(
                {"error": "Hospital ID is required in headers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            patient = PatientDetails.objects.get(email=email, hospital__hospital_id=hospital_id)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found"}, status=400)

        if not patient.verified_at:
            return Response({"error": "Please verify OTP first"}, status=400)

        if not patient.is_active_patient:
            return Response({"error": "Account disabled"}, status=403)

        if not check_password(password, patient.password):
            return Response({"error": "Incorrect password"}, status=400)

        payload = {
            'patient_id': patient.id,
            'email': patient.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            "message": "Login successful",
            "token": token,
            "patient": PatientDetailsSerializer(patient).data,
            "hospital": HospitalSerializer(patient.hospital).data
        }, status=200)

class PatientForgotPasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            patient = PatientDetails.objects.get(email=email)
            otp = random.randint(100000, 999999)
            patient.email_otp = otp
            patient.save()

            send_mail(
                subject="Reset Password OTP",
                message=f"Your One-Time Password (OTP) for completing your reset password is:  {otp}",
                from_email=os.getenv('EMAIL_HOST_USER'),
                recipient_list=[email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent to your email", "patient_id": patient.id}, status=200)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found with this email"}, status=404)
        
class PatientVerifyOTPAPIView(APIView):
    def post(self, request):
        patient_id = request.data.get("patient_id")
        otp = request.data.get("otp")

        try:
            patient = PatientDetails.objects.get(id=patient_id, email_otp=otp)
            patient.email_otp = None  # clear OTP after verification
            patient.verified_at = timezone.now()
            patient.save()

            return Response({"message": "OTP verified successfully"}, status=200)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Invalid OTP or patient ID"}, status=400)

    
class PatientResetPasswordAPIView(APIView):
    def post(self, request):
        patient_id = request.data.get("patient_id")
        new_password = request.data.get("new_password")

        if not all([patient_id, new_password]):
            return Response({"error": "Patient ID and new password are required"}, status=400)

        try:
            patient = PatientDetails.objects.get(id=patient_id)
            patient.password = make_password(new_password)
            patient.save()

            return Response({"message": "Password reset successfully"}, status=200)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Invalid patient ID"}, status=404)

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
        opd_type = request.data.get("opd_type", "normal")

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
            visit_count=patient.visit_count,  # set updated count
            opd_type=opd_type
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

        # --- ✅ TODAY's DATE RANGE ---
        today = timezone.localdate()
        tz = timezone.get_current_timezone()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=tz)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=tz)

        # --- ✅ FETCH ONLY TODAY's OPDs ---
        today_opds = OPD.objects.filter(
            hospital=hospital,
            date_time__range=(start_of_day, end_of_day)
        ).order_by('-date_time')

        serializer = OPDSerializer(today_opds, many=True)

        # --- ✅ TODAY's STATS ---
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
            "count": total_today,
            "message": "Today's OPD records fetched successfully",
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

        # Get start and end of today
        today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Only today's OPD records
        today_opds = OPD.objects.filter(
            doctor_id=doctor_id,
            hospital=hospital,
            date_time__gte=today_start,
            date_time__lt=today_end
        ).order_by('-date_time')

        total_today = today_opds.count()
        waiting_count = today_opds.filter(status='waiting').count()
        out_count = today_opds.filter(status='out').count()
        completed_count = today_opds.filter(status='completed').count()

        def percent(part):
            return round((part / total_today) * 100, 2) if total_today > 0 else 0

        today_stats = {
            "waiting_percentage": percent(waiting_count),
            "out_percentage": percent(out_count),
            "completed_percentage": percent(completed_count)
        }

        return Response({
            "message": "Today's OPD records fetched successfully.",
            "data": OPDSerializer(today_opds, many=True).data,
            "today_stats": today_stats,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class DoctorPastOPDView(APIView):
    def get(self, request, doctor_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Today's date range
        today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # OPDs excluding today
        past_opds = OPD.objects.filter(
            doctor_id=doctor_id,
            hospital=hospital
        ).exclude(
            date_time__gte=today_start,
            date_time__lt=today_end
        ).order_by('-date_time')

        return Response({
            "count": past_opds.count(),
            "message": "Past OPD records (excluding today) fetched successfully.",
            "data": OPDSerializer(past_opds, many=True).data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)
    
class AllPastOPDView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Today's date range
        today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Past OPDs (all doctors) excluding today
        past_opds = OPD.objects.filter(
            hospital=hospital
        ).exclude(
            date_time__gte=today_start,
            date_time__lt=today_end
        ).order_by('-date_time')

        return Response({
            "count": past_opds.count(),
            "message": "Past OPD records for all doctors (excluding today) fetched successfully.",
            "data": OPDSerializer(past_opds, many=True).data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class TodayOPDListView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        # Get hospital
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Today's date range
        today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Filter OPD for today
        todays_opds = OPD.objects.filter(
            hospital=hospital,
            date_time__gte=today_start,
            date_time__lt=today_end
        ).order_by("date_time")

        return Response({
            "message": "Today's OPD records fetched successfully.",
            "count": todays_opds.count(),
            "data": OPDSerializer(todays_opds, many=True).data,
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
            pharmacy_medicine_id = item.get('pharmacy_medicine_id')  # ✅ NEW
            pharmacy_medicine = None

            if pharmacy_medicine_id:
                try:
                    pharmacy_medicine = PharmacyMedicine.objects.get(id=pharmacy_medicine_id, hospital=hospital)
                except PharmacyMedicine.DoesNotExist:
                    return Response({"error": f"PharmacyMedicine with id {pharmacy_medicine_id} not found in this hospital."},
                                    status=status.HTTP_404_NOT_FOUND)

            PrescriptionItem.objects.create(
                prescription=prescription,
                # medicine_name=item['medicine_name'],
                dosage=item['dosage'],
                duration_days=item['duration_days'],
                instruction=item.get('instruction', ''),
                quantity=item.get('quantity'),                      # Optional
                pharmacy_medicine=pharmacy_medicine,                # ✅ NEW
                hospital=hospital                                   # ✅ NEW
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

class PrescriptionPaymentUpdateAPIView(APIView):
    def patch(self, request, pk):
        try:
            prescription = Prescription.objects.get(pk=pk)
        except Prescription.DoesNotExist:
            return Response({"error": "Prescription not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prevent update if already paid
        if prescription.status == "paid":
            return Response({
                "error": "This prescription is already marked as paid and cannot be modified."
            }, status=status.HTTP_400_BAD_REQUEST)

        payment_mode = request.data.get("payment_mode")
        payment_status = request.data.get("payment_status")

        if not payment_mode or not payment_status:
            return Response({"error": "Both payment_mode and payment_status are required."}, status=status.HTTP_400_BAD_REQUEST)

        prescription.payment_mode = payment_mode
        prescription.status = payment_status
        prescription.date_time = timezone.now()
        prescription.save()

        return Response({
            "message": "Prescription payment updated successfully.",
            "prescription": PrescriptionSerializer(prescription).data
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
        ).values_list('pharmacy_medicine__medicine_name', flat=True).distinct()

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

class SupplierCreateAPIView(APIView):
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

        serializer = SupplierSerializer(data=data)
        if serializer.is_valid():
            serializer.save(hospital=hospital)
            return Response({
                "message": "Supplier added successfully.",
                "data": serializer.data,
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

        suppliers = Supplier.objects.filter(hospital=hospital).order_by('-purchase_date_time')
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PharmacyBillCreateAPIView(APIView):
    def post(self, request):
        data = request.data
        hospital_id = request.headers.get("Hospital-Id")

        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=400)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=404)

        patient_id = data.get('patient_id')
        user_id = data.get('user_id')
        medical_items = data.get('medical_items', [])
        prescription_id = data.get('prescription_id')
        prescription = None

        if prescription_id:
            try:
                prescription = Prescription.objects.get(id=prescription_id, hospital=hospital)
            except Prescription.DoesNotExist:
                return Response({"error": "Prescription not found for this hospital."}, status=404)

        if not all([patient_id, user_id, medical_items]):
            return Response({"error": "patient_id, user_id, and medical_items are required."}, status=400)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found in this hospital."}, status=404)

        try:
            doctor = HMSUser.objects.get(id=user_id, hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"error": "User not found in this hospital."}, status=404)

        try:
            total_amount = sum(
                float(item['amount']) * int(item.get('quantity', 1))
                for item in medical_items
                if 'amount' in item
            )
        except Exception:
            return Response({"error": "Invalid medical_items format."}, status=400)

        with transaction.atomic():
            for item in medical_items:
                name = item.get('name')
                dosage = item.get('dosage')
                quantity_to_deduct = int(item.get('quantity', 0))

                if not name or not dosage:
                    return Response({"error": "Each item must include 'name' and 'dosage'."}, status=400)

                # 🔍 Find PharmacyMedicine by name + dosage + hospital
                try:
                    pharmacy_medicine = PharmacyMedicine.objects.get(
                        hospital=hospital,
                        medicine_name=item['name'],
                        # medicine_unit=item['dosage']
                    )
                except PharmacyMedicine.DoesNotExist:
                    return Response({
                        "error": f"Pharmacy medicine '{item['name']}' not found."
                    }, status=404)

                # 🔍 Find stock entry
                try:
                    stock = MedicineStock.objects.select_for_update().filter(
                        medicine=pharmacy_medicine,
                        hospital=hospital
                    ).order_by('-id').first()
                    if not stock or stock.quantity < quantity_to_deduct:
                        return Response({
                            "error": f"Not enough stock for {name}. Available: {stock.quantity if stock else 0}, Required: {quantity_to_deduct}"
                        }, status=400)
                except MedicineStock.DoesNotExist:
                    return Response({"error": f"No stock found for {name}."}, status=404)

                # ➖ Deduct stock
                stock.quantity -= quantity_to_deduct
                stock.save()

                # 🧾 Log stock transaction
                StockTransaction.objects.create(
                    hospital=hospital,
                    medicine_stock=stock,
                    transaction_type='OUT',
                    quantity=quantity_to_deduct,
                    transaction_date=timezone.now(),
                    notes="Deducted on pharmacy bill"
                )

                # ✅ Replace in item for saving accurate reference
                item['medicine_stock_id'] = stock.id

        # 🧾 Create Bill
        bill = PharmacyBill.objects.create(
            hospital=hospital,
            patient=patient,
            doctor=doctor,
            date_issued=data.get('date_issued'),
            medical_items=medical_items,
            total_amount=total_amount,
            payment_status='unpaid',
            prescription=prescription,
            payment_mode=None,
            payment_date=None
        )

        serializer = PharmacyBillSerializer(bill)
        return Response({
            "message": "Pharmacy Bill created successfully.",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=201)

class UpdatePharmacyBillPaymentView(APIView):
    def patch(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Get pharmacy bill by id and hospital
        try:
            bill = PharmacyBill.objects.get(id=pk, hospital=hospital)
        except PharmacyBill.DoesNotExist:
            return Response({"error": "Pharmacy bill not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)

        # Already paid?
        if bill.payment_status == "paid":
            return Response({"error": "Payment is already marked as paid and cannot be changed.."}, status=status.HTTP_400_BAD_REQUEST)

        # Get payment mode from request
        payment_mode = request.data.get("payment_mode")
        payment_status = request.data.get("payment_status")
        patient_id = request.data.get("patient_id")

        if not payment_mode or not payment_status:
            return Response({"error": "Both payment_mode and payment_status are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get patient if provided
        patient = None
        if patient_id:
            try:
                patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
            except PatientDetails.DoesNotExist:
                return Response({"error": "Patient not found in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        # Update fields
        bill.payment_status = payment_status
        bill.payment_mode = payment_mode
        bill.payment_date = timezone.now()
        bill.save()

         # Create Invoice
        invoice = InvoicePharmacyBill.objects.create(
            bill=bill,
            patient=bill.patient,
            payment_mode=payment_mode,
            paid_amount=bill.total_amount,
            medical_items=bill.medical_items
        )

        serializer = PharmacyBillSerializer(bill)
        return Response({
            "message": "Pharmacy bill payment updated and invoice generated successfully.",
            "data": serializer.data,
            "invoice": InvoicePharmacyBillSerializer(invoice).data,
            # "invoice":
            # {
            #     "id": invoice.id,
            #     "bill": bill.id,
            #     "patient": {
            #         "id": patient.id if patient else None,
            #         "name": patient.full_name
            #     },
            #     "paid_amount": invoice.paid_amount,
            #     "payment_mode": invoice.payment_mode,
            #     "date": invoice.date,
            #     "medical_items": invoice.medical_items
            # },
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

# get invoice with pharmacy bill 
class PharmacyInvoiceListView(APIView):
    def get(self, request):
        # ✅ Get Hospital ID from Headers
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Get Hospital object
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Get invoices only for this hospital
        invoices = InvoicePharmacyBill.objects.filter(
            bill__hospital=hospital
        ).select_related("bill", "patient").order_by("-date")

        serializer = InvoicePharmacyBillSerializer(invoices, many=True)

        return Response({
            "message": "All pharmacy invoices fetched successfully",
            "count": invoices.count(),
            "invoices": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

# Stock of pharmacy
class PharmacyMedicineCreateView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=400)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=404)

        data = request.data.copy()
        data['hospital'] = hospital.id

        serializer = PharmacyMedicineSerializer(data=data)
        if serializer.is_valid():
            serializer.save(hospital=hospital)
            return Response({
                "message": "Pharmacy medicine created successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data
            }, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=400)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=404)

        medicines = PharmacyMedicine.objects.filter(hospital=hospital)
        serializer = PharmacyMedicineSerializer(medicines, many=True)

        return Response({
            "message": "Pharmacy medicines fetched successfully.",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=200)
    
class MedicineStockCreateView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=400)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=404)

        data = request.data.copy()
        data['hospital'] = hospital.id

        medicine_id = data.get('medicine')
        batch_number = data.get('batch_number')

        # ✅ Check for existing stock with same medicine + batch in this hospital
        if MedicineStock.objects.filter(hospital=hospital, medicine_id=medicine_id, batch_number=batch_number).exists():
            return Response(
                {"error": "Stock for this medicine with the same batch number already exists."},
                status=400
            )

        serializer = MedicineStockSerializer(data=data)
        if serializer.is_valid():
            stock = serializer.save(hospital=hospital)
            # serializer.save(hospital=hospital)

            # Create IN type stock transaction
            stock_transaction = StockTransaction.objects.create(
                medicine_stock=stock,
                transaction_type='IN',
                quantity=stock.quantity,
                transaction_date=timezone.now(),
                notes="Stock added",
                hospital=hospital
            )
            # for showing the transaction in response
            transaction_data = StockTransactionSerializer(stock_transaction).data

            return Response({
                "message": "Medicine stock added successfully.",
                "data": serializer.data,
                "transaction": transaction_data,
                "hospital": HospitalSerializer(hospital).data
            }, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=400)
        
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=404)

        stocks = MedicineStock.objects.filter(hospital=hospital).order_by('-last_updated')
        serializer = MedicineStockSerializer(stocks, many=True)
        return Response({"medicine_stock": serializer.data}, status=200)

class StockTransactionListView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        transactions = StockTransaction.objects.filter(medicine_stock__hospital=hospital).order_by('-transaction_date')
        serializer = StockTransactionSerializer(transactions, many=True)
        return Response({"transactions": serializer.data}, status=200)

class PrescriptionWithBillAPIView(APIView):
    def get(self, request):
        patient_id = request.query_params.get('patient_id')
        hospital_id = request.headers.get('Hospital-Id')

        if not hospital_id or not patient_id:
            return Response({"error": "Hospital-Id header and patient_id query param are required."}, status=400)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID"}, status=404)

        # Get all prescriptions for patient (even if no bill exists)
        prescriptions = Prescription.objects.filter(
            patient_id=patient_id,
            hospital=hospital
        ).prefetch_related('pharmacy_bills').order_by('-date_issued')  # ← this enables reverse FK access

        data = []
        for prescription in prescriptions:
            serialized_prescription = PrescriptionSerializer(prescription).data
            # Get associated bills (if any)
            bills = prescription.pharmacy_bills.all()
            serialized_prescription['pharmacy_bills'] = PharmacyBillSerializer(bills, many=True).data
            data.append(serialized_prescription)

        return Response({
            "count": len(data),
            "prescriptions": data}, status=200)

class DoctorTimetableCreateAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]  # Optional: Add permission if required

    def post(self, request):
        hospital_id = request.headers.get('hospital_id')
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['hospital'] = hospital.id  # Pass PK to serializer

        serializer = DoctorTimetableSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DoctorTimetableByDoctorAPIView(APIView):
    def get(self, request, doctor_id):
        hospital_id = request.headers.get('hospital_id')

        if not hospital_id:
            return Response({"error": "hospital_id header is required"}, status=status.HTTP_400_BAD_REQUEST)

        timetables = DoctorTimetable.objects.filter(doctor_id=doctor_id, hospital__hospital_id=hospital_id)
        
        if not timetables.exists():
            return Response({"message": "No timetable found for this doctor in this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorTimetableSerializer(timetables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateDoctorTimetableAPIView(APIView):
    def put(self, request, pk):
        hospital_id = request.headers.get('hospital_id')
        if not hospital_id:
            return Response({"error": "hospital_id header is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            timetable = DoctorTimetable.objects.get(id=pk, hospital__hospital_id=hospital_id)
        except DoctorTimetable.DoesNotExist:
            return Response({"error": "Timetable not found for this hospital."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorTimetableSerializer(timetable, data=request.data, partial=True)

        if serializer.is_valid():
            # Validation: start_time < end_time
            start_time = serializer.validated_data.get("start_time", timetable.start_time)
            end_time = serializer.validated_data.get("end_time", timetable.end_time)

            if start_time >= end_time:
                return Response({"error": "start_time must be less than end_time."}, status=status.HTTP_400_BAD_REQUEST)

            # Validation: prevent overlapping time for same doctor & date
            doctor = serializer.validated_data.get("doctor", timetable.doctor)
            date = serializer.validated_data.get("date", timetable.date)

            overlapping = DoctorTimetable.objects.filter(
                doctor=doctor,
                hospital=timetable.hospital,
                date=date
            ).exclude(id=timetable.id).filter(
                start_time__lt=end_time,
                end_time__gt=start_time
            )

            if overlapping.exists():
                return Response({"error": "Overlapping time slot exists for this doctor."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreatePatientAppointmentAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        patient_id = request.data.get("patient_id")
        if not patient_id:
            return Response({"error": "Patient ID is required"}, status=400)

        try:
            patient = PatientDetails.objects.get(id=patient_id)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Invalid Patient ID"}, status=404)

        preferred_doctor_id = request.data.get("preferred_doctor")
        if not preferred_doctor_id:
            return Response({"error": "Preferred doctor is required"}, status=400)

        try:
            preferred_doctor = HMSUser.objects.get(id=preferred_doctor_id, designation='doctor')
        except HMSUser.DoesNotExist:
            return Response({"error": "Invalid doctor ID or user is not a doctor"}, status=404)

        serializer = PatientAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                hospital=hospital, 
                patient=patient, 
                preferred_doctor=preferred_doctor,
                final_time=None)  # Final time = None on creation
            return Response({
                "message": "Appointment requested successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorAppointmentsAPIView(APIView):
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
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        appointments = PatientAppointment.objects.filter(hospital=hospital,preferred_doctor=doctor).order_by('-created_at')
        serializer = PatientAppointmentSerializer(appointments, many=True)
        return Response({
            "message": f"Appointments for Doctor ID {doctor_id} fetched successfully.",
            "count": appointments.count(),
            "appointments":serializer.data,
            "hospital": HospitalSerializer(hospital).data,
            }, status=status.HTTP_200_OK)

class PatientAppointmentsAPIView(APIView):
    def get(self, request, patient_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            patient = PatientDetails.objects.get(id=patient_id)
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch appointments
        appointments = PatientAppointment.objects.filter(
            hospital=hospital,
            patient=patient
        ).select_related('preferred_doctor').order_by('-created_at')

        appointment_data = []
        for appointment in appointments:
            # Serialize appointment
            appointment_dict = PatientAppointmentSerializer(appointment).data

            # Get Doctor Profile if available
            doctor = appointment.preferred_doctor
            if doctor:
                try:
                    doctor_profile = DoctorProfile.objects.get(doctor=doctor, hospital=hospital)
                    appointment_dict["doctor_profile"] = DoctorProfileSerializer(doctor_profile).data
                except DoctorProfile.DoesNotExist:
                    appointment_dict["doctor_profile"] = None
            else:
                appointment_dict["doctor_profile"] = None

            appointment_data.append(appointment_dict)

        return Response({
            "message": "Appointments fetched successfully.",
            "count": len(appointment_data),
            "appointments": appointment_data,
            "hospital": HospitalSerializer(hospital).data,
        }, status=status.HTTP_200_OK)

class AppointmentStatusUpdateView(APIView):
    def patch(self, request, appointment_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            appointment = PatientAppointment.objects.get(id=appointment_id, hospital=hospital)
        except PatientAppointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=http_status.HTTP_404_NOT_FOUND)

        serializer = AppointmentStatusUpdateSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            new_status = validated_data.get("status", appointment.status)
            new_patient_status = validated_data.get("patient_status", appointment.patient_status)

            # 1. Case: Patient cancels after reschedule by marking not available
            if appointment.status == 'rescheduled' and new_patient_status == 'not_available':
                appointment.status = 'cancelled'
                appointment.status_remark = validated_data.get("status_remark", "Cancelled by patient (not available after reschedule)")
                appointment.patient_status = 'not_available'
                # appointment.final_status = False
                appointment.save()
                return Response({
                    "message": "Appointment cancelled by patient after reschedule.", 
                    "data": AppointmentStatusUpdateSerializer(appointment).data,
                    "hospital": HospitalSerializer(hospital).data,
                    }, status=http_status.HTTP_200_OK)

            # 2. Case: Patient cancels before doctor responds
            if new_status == "cancelled" and appointment.status == "requested":
                appointment.status = 'cancelled'
                appointment.status_remark = validated_data.get("status_remark", "Cancelled by patient before doctor's response.")
                # appointment.final_status = False
                appointment.save()
                return Response({"message": "Appointment cancelled by patient.", 
                                 "data": AppointmentStatusUpdateSerializer(appointment).data,
                                 "hospital": HospitalSerializer(hospital).data,
                                 }, status=http_status.HTTP_200_OK)

            # 3. Normal update flow
            serializer.save()
            # Send email notification to patient
            self.send_appointment_email(appointment)
            return Response({
                "message": "Appointment updated successfully.",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data,
                }, status=http_status.HTTP_200_OK)

        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
    
    def send_appointment_email(self, appointment):
        """Send email to patient when doctor responds."""
        patient_email = appointment.patient.email
        doctor_name = appointment.preferred_doctor.name
        hospital_name = appointment.hospital.name
        hospital_logo_url = appointment.hospital.logo.url if appointment.hospital.logo else None
        status_message = appointment.get_status_display()  # Human-readable status

        subject = f"Appointment Update from Dr. {doctor_name}"
          # Message body
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            {"<img src='" + hospital_logo_url + "' alt='Hospital Logo' style='max-height: 80px; margin-bottom: 20px;'/>" if hospital_logo_url else ""}
            <h2 style="color: #2c3e50;">Appointment Update - {hospital_name}</h2>
            <p>Dear <strong>{appointment.patient.full_name}</strong>,</p>
            <p>Your appointment request with <strong>Dr. {doctor_name}</strong> has been <strong>{status_message}</strong>.</p>
        """

        # Add extra info depending on status
        if appointment.status in ["accepted", "rescheduled"] and appointment.final_time:
            label = "Final appointment time" if appointment.status == "accepted" else "New suggested time"
            html_content += f"<p><strong>{label}:</strong> {appointment.final_time.strftime('%Y-%m-%d %H:%M')}</p>"
        elif appointment.status == "rejected":
            html_content += "<p>Unfortunately, your appointment request has been rejected.</p>"

         # Add doctor's remark
        if appointment.status_remark:
            html_content += f"<p><strong>Doctor's Remark:</strong> {appointment.status_remark}</p>"

        # Closing message
        html_content += f"""
            <p>Thank you,<br><strong>{hospital_name}</strong></p>
        </div>
        """

        # Send as HTML email
        email = EmailMultiAlternatives(
            subject,
            "",  # Plain text fallback
            settings.DEFAULT_FROM_EMAIL,
            [patient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
    
class PatientAppointmentResponseAPIView(APIView):
    def patch(self, request, pk):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            appointment = PatientAppointment.objects.get(pk=pk, hospital=hospital)
        except PatientAppointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientAppointmentResponseSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            new_status = validated_data.get("status", appointment.status)
            new_patient_status = validated_data.get("patient_status", appointment.patient_status)

            # ✅ If doctor already rescheduled and patient says 'not available', mark as cancelled
            if appointment.status == 'rescheduled' and new_patient_status == 'not_available':
                appointment.status = 'cancelled'
                appointment.patient_status = 'not_available'
                appointment.status_remark = validated_data.get("status_remark", "Cancelled by patient after reschedule.")
                appointment.final_status = False
                appointment.save()
                return Response({
                    "message": "Appointment cancelled by patient after reschedule.",
                    "data": PatientAppointmentResponseSerializer(appointment).data,
                    "hospital": HospitalSerializer(hospital).data,
                }, status=status.HTTP_200_OK)
            
            if new_status == "cancelled" and appointment.status == "requested":
                appointment.status = 'cancelled'
                appointment.status_remark = validated_data.get("status_remark", "Cancelled by patient before doctor's response.")
                # appointment.final_status = False
                appointment.save()
                return Response({"message": "Appointment cancelled by patient.", 
                                 "data": AppointmentStatusUpdateSerializer(appointment).data,
                                 "hospital": HospitalSerializer(hospital).data,
                                 }, status=http_status.HTTP_200_OK)

            # 🔁 Normal case: patient updates status without triggering cancellation
            serializer.save()
            return Response({
                "message": "Patient response recorded successfully",
                "data": serializer.data,
                "hospital": HospitalSerializer(hospital).data,
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientCancelAppointmentAPIView(APIView):
    def patch(self, request, appointment_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            appointment = PatientAppointment.objects.get(id=appointment_id, hospital=hospital)
        except PatientAppointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=http_status.HTTP_404_NOT_FOUND)

        if appointment.status != 'requested':
            return Response(
                {"error": "Appointment can only be cancelled before the doctor responds (status must be 'requested')."},
                status=http_status.HTTP_400_BAD_REQUEST
            )

        appointment.status = 'cancelled'
        appointment.final_status = False
        appointment.status_remark = request.data.get('status_remark', 'Cancelled by patient before doctor response')
        appointment.save()

        return Response({
            "message": "Appointment cancelled successfully by patient.",
            "data": PatientAppointmentSerializer(appointment).data,
            "hospital": HospitalSerializer(hospital).data,
        }, status=http_status.HTTP_200_OK)


# Lab assistance - 
class LabReportCreateAPIView(APIView):
    def post(self, request):
        try:
            hospital_id = request.headers.get("Hospital-Id")
            if not hospital_id:
                return Response({"error": "Hospital ID is required in headers."}, status=http_status.HTTP_400_BAD_REQUEST)

            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital ID."}, status=http_status.HTTP_404_NOT_FOUND)

        # Extract patient and uploader
        patient_id = request.data.get("patient")
        uploaded_by_id = request.data.get("uploaded_by")

        if not patient_id or not uploaded_by_id:
            return Response({"error": "Both 'patient' and 'uploaded_by' fields are required."}, status=http_status.HTTP_400_BAD_REQUEST)

        try:
            patient = PatientDetails.objects.get(id=patient_id, hospital=hospital)
            uploaded_by = HMSUser.objects.get(id=uploaded_by_id, hospital=hospital)
        except (PatientDetails.DoesNotExist, HMSUser.DoesNotExist):
            return Response({"error": "Invalid patient or uploaded_by for this hospital."}, status=http_status.HTTP_404_NOT_FOUND)

        # Create lab report
        serializer = LabReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hospital = hospital, patient=patient, uploaded_by=uploaded_by)
            return Response({"message": "Lab report uploaded successfully.", "data": serializer.data}, status=http_status.HTTP_201_CREATED)

        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
    
class LabReportsByLabAssistantAPIView(APIView):
    def get(self, request, lab_assistant_id):
        hospital_id = request.headers.get("hospital_id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=http_status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital ID."}, status=http_status.HTTP_404_NOT_FOUND)

        try:
            lab_assistant = HMSUser.objects.get(id=lab_assistant_id, designation='lab_assistant', hospital=hospital)
        except HMSUser.DoesNotExist:
            return Response({"error": "Lab Assistant not found for this hospital."}, status=http_status.HTTP_404_NOT_FOUND)

        lab_reports = LabReport.objects.filter(uploaded_by=lab_assistant)
        serializer = LabReportSerializer(lab_reports, many=True)

        return Response({"lab_reports": serializer.data}, status=http_status.HTTP_200_OK)

class LabReportDeleteAPIView(APIView):
    def delete(self, request, report_id):
        hospital_id = request.headers.get("hospital_id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=http_status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital ID."}, status=http_status.HTTP_404_NOT_FOUND)

        try:
            lab_report = LabReport.objects.get(id=report_id, hospital=hospital)
        except LabReport.DoesNotExist:
            return Response({"error": "Lab report not found in this hospital."}, status=http_status.HTTP_404_NOT_FOUND)

        lab_report.delete()
        return Response({"message": "Lab report deleted successfully."}, status=http_status.HTTP_200_OK)


# for birth report
class BirthRecordCreateView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("hospital_id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital_id."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["hospital"] = hospital.id

        serializer = BirthRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save(hospital=hospital)
            return Response({
                "message": "Birth report created successfully",
                "data":serializer.data,
                "hospital":HospitalSerializer(hospital).data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        hospital_id = request.headers.get("hospital_id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital_id."}, status=status.HTTP_404_NOT_FOUND)

        birth_records = BirthRecord.objects.filter(hospital=hospital)
        serializer = BirthRecordSerializer(birth_records, many=True)
        return Response({
                "message": "Birth report Fetch successfully",
                "data":serializer.data,
                "hospital":HospitalSerializer(hospital).data
                }, status=status.HTTP_200_OK)

class DeathReportCreateView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("hospital_id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital_id."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['hospital'] = hospital.id  # Use the primary key

        serializer = DeathReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save(hospital=hospital)
            return Response({
                "message": "Death report created successfully",
                "data": serializer.data,
                "hospital":HospitalSerializer(hospital).data, 
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        hospital_id = request.headers.get("hospital_id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid hospital_id."}, status=status.HTTP_404_NOT_FOUND)

        death_reports = DeathReport.objects.filter(hospital=hospital)
        serializer = DeathReportSerializer(death_reports, many=True)
        return Response({
                "message": "Death report Fetch successfully",
                "data":serializer.data,
                "hospital":HospitalSerializer(hospital).data
                }, status=status.HTTP_200_OK)


# get all counts 
class HospitalDashboardStatsAPIView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59)

        todays_opd_count = OPD.objects.filter(hospital=hospital, date_time__range=(today_start, today_end)).count()
        todays_ipd_count = IPD.objects.filter(hospital=hospital, admit_date__range=(today_start, today_end)).count()
        total_patient_count = PatientDetails.objects.filter(hospital=hospital).count()

        doctors_count = HMSUser.objects.filter(hospital=hospital, designation__iexact="doctor").count()
        nurses_count = HMSUser.objects.filter(hospital=hospital, designation__iexact="nurse").count()
        receptionist_count = HMSUser.objects.filter(hospital=hospital, designation__iexact="receptionist").count()
        lab_assistant_count = HMSUser.objects.filter(hospital=hospital, designation__iexact="lab_assistant").count()
        pharmacist_count = HMSUser.objects.filter(hospital=hospital, designation__iexact="pharmacist").count()

        return Response({
            "hospital": HospitalSerializer(hospital).data,
            "todays_opd_count": todays_opd_count,
            "todays_ipd_count": todays_ipd_count,
            "total_patient_count": total_patient_count,
            "doctors_count": doctors_count,
            "nurses_count": nurses_count,
            "receptionist_count": receptionist_count,
            "lab_assistant_count": lab_assistant_count,
            "pharmacist_count": pharmacist_count
        }, status=status.HTTP_200_OK)

class PharmacyOutBillCreateAPIView(APIView):
    def post(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID"}, status=status.HTTP_404_NOT_FOUND)

        patient_name = request.data.get("patient_name")
        note = request.data.get("note", "")
        medicine_items = request.data.get("medicine_items", [])

        if not patient_name or not medicine_items:
            return Response({"error": "Patient name and medicine items are required"}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = Decimal("0.00")

        for item in medicine_items:
            name = item.get("name")
            quantity = int(item.get("quantity", 0))

            if not name or quantity <= 0:
                return Response({"error": "Medicine name and valid quantity are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Get stock item
            try:
                stock_item = MedicineStock.objects.get(
                    hospital=hospital,
                    medicine__medicine_name__iexact=name
                )
            except MedicineStock.DoesNotExist:
                return Response({"error": f"Medicine '{name}' not found in stock."}, status=status.HTTP_404_NOT_FOUND)

            # Check stock quantity
            if stock_item.quantity < quantity:
                return Response({"error": f"Not enough stock for '{name}'. Available: {stock_item.quantity}"}, status=status.HTTP_400_BAD_REQUEST)

            # Get selling price
            price_per_unit = stock_item.selling_price
            item_total = price_per_unit * quantity
            total_amount += item_total

            # Store amount back to item
            item["amount"] = float(price_per_unit)

            # Deduct stock
            stock_item.quantity -= quantity
            stock_item.save()

        # Save bill
        bill = PharmacyOutBill.objects.create(
            hospital=hospital,
            patient_name=patient_name,
            note=note,
            medicine_items=medicine_items,  # JSON
            total_amount=total_amount,
            payment_status='unpaid',
            payment_mode=None,
            payment_date=None
        )

        bill_serializer = PharmacyOutBillSerializer(bill)

        return Response({
            "message": "Pharmacy out-patient bill created successfully",
            "bill": bill_serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_201_CREATED)
    

    def get(self, request):
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
                {"error": "Invalid Hospital ID"},
                status=status.HTTP_404_NOT_FOUND
            )

        bills = PharmacyOutBill.objects.filter(hospital=hospital).order_by("-id")
        serializer = PharmacyOutBillSerializer(bills, many=True)

        return Response({
            "count": bills.count(),
            "message": "Pharmacy out-patient bills fetched successfully",
            "data": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class PharmacyOutBillUpdateAPIView(APIView):
    def patch(self, request, bill_id):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        # Get hospital
        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        # Get bill
        try:
            bill = PharmacyOutBill.objects.get(id=bill_id, hospital=hospital)
        except PharmacyOutBill.DoesNotExist:
            return Response({"error": "Bill not found."}, status=status.HTTP_404_NOT_FOUND)

         # Already paid check
        if bill.payment_status == "paid":
            return Response({"error": "Payment is already marked as paid."}, status=status.HTTP_400_BAD_REQUEST)


        payment_mode = request.data.get("payment_mode")
        payment_status = request.data.get("payment_status")

        if not payment_mode or not payment_status:
            return Response({"error": "Both payment_mode and payment_status are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Update bill payment details
        bill.payment_status = payment_status
        bill.payment_mode = payment_mode
        bill.payment_date = timezone.now()
        bill.save()

         # If payment is completed, create invoice
        if payment_status.lower() == "paid":
            invoice = PharmacyOutInvoice.objects.create(
                bill=bill,
                patient_name=bill.patient_name,
                payment_mode=payment_mode,
                paid_amount=bill.total_amount,
                medicine_items=bill.medicine_items
            )

            invoice_data = PharmacyOutInvoiceSerializer(invoice).data
        else:
            invoice_data = None

        return Response({
            "message": "Pharmacy out-patient bill updated successfully",
            "bill": PharmacyOutBillSerializer(bill).data,
            "invoice": invoice_data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)

class GetAllPharmacyOutInvoicesView(APIView):
    def get(self, request):
        hospital_id = request.headers.get("Hospital-Id")
        if not hospital_id:
            return Response({"error": "Hospital ID is required in headers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hospital = Hospital.objects.get(hospital_id=hospital_id)
        except Hospital.DoesNotExist:
            return Response({"error": "Invalid Hospital ID."}, status=status.HTTP_404_NOT_FOUND)

        invoices = PharmacyOutInvoice.objects.filter(bill__hospital=hospital).order_by("-date")
        serializer = PharmacyOutInvoiceSerializer(invoices, many=True)

        return Response({
            "message": "Pharmacy Out Bill Invoices fetched successfully.",
            "count": invoices.count(),
            "invoices": serializer.data,
            "hospital": HospitalSerializer(hospital).data
        }, status=status.HTTP_200_OK)