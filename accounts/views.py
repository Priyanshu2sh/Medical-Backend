import random
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import User, CounsellorProfile
from .serializers import UserSerializer, CounsellorProfileSerializer, CounsellorProfileUpdateSerializer
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.conf import settings
import jwt
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from .utils import generate_password_reset_token
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import NotAuthenticated
from assessments.models import MedicalHealthUser


# Create your views here.
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        # Attach user to request for further use
        return (user, None)


class RegisterUser(APIView):

    def post(self, request):
        data = request.data
        # print(data)
        email = data.get('email')
        r_level = data.get('r_level')
        role = data.get('role')

        # Validate role (optional)
        if role not in dict(User.role_choices).keys():
            return Response(
                {'error': 'Invalid role'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data=data)

        try:
            # Check if a user with this email already exists
            existing_user = User.objects.get(email=email)
            if existing_user.verified_at is None:
                # If the user exists but is not verified, update details and resend OTP
                email_otp = random.randint(100000, 999999)

                existing_user.email_otp = email_otp
                existing_user.save()

                # Resend OTP
                send_mail(
                    'Your OTP for Registration',
                    f'Your OTP is {email_otp}',
                    'noreply@example.com',
                    [existing_user.email],
                    fail_silently=False,
                )
                return Response({'message': 'OTP resent to your email.', 'user_id': existing_user.id}, status=status.HTTP_200_OK)
            else:
                # If the user is verified, inform the user they cannot register again
                return Response({'error': 'Email is already registered and verified. Please log in.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            # If no existing user is found, proceed with registration

            if serializer.is_valid():
                user = serializer.save()
                user.r_level = r_level

                # Send OTP
                email_otp = random.randint(100000, 999999)
                user.email_otp = email_otp
                user.save()

                # Send OTP to the user's email
                send_mail(
                    'Your OTP for Registration',
                    f'Your OTP is {email_otp}',
                    'noreply@example.com',
                    [user.email],
                    fail_silently=False,
                )

                return Response({
                    'message': 'OTP sent to your email',
                    'user_id': user.id, 
                    "r_level":r_level,
                    'is_active': user.is_active 
                },status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        email_otp = request.data.get('email_otp')        

        try:
            user = User.objects.get(id=user_id, email_otp=email_otp, verified_at__isnull=True)
            user.verified_at = now()  # Set the verified timestamp
            user.email_otp = None  # Clear the OTP field
            user.save()
            return Response({'message': 'User verified successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Invalid OTP, or user already verified'}, status=status.HTTP_400_BAD_REQUEST)

class LoginUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate email and password fields
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        elif not password:
            return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': f'Email ({email}) not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify password
        if not check_password(password, user.password):
            return Response({'error': f'Email ({email}) found but password incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if account is disabled
        if not user.is_active:
            return Response({'error': 'Your account is disabled. Please contact admin.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user is verified (Consumer)
        if user.verified_at is None:
            return Response({'error': 'Please verify your email before logging in'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT Token
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        # Serialize user data using UserSerializer
        user_data = UserSerializer(user).data
        user_data['r_level'] = user.r_level 

        return Response({
            'message': 'Login successfully',
            'token': token,
            'user': user_data
        }, status=status.HTTP_200_OK)
    

class CompleteCounsellorProfile(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    permission_classes = []  # No authentication required

    def post(self, request):
        # Validate user_id exists
        try:
            user = MedicalHealthUser.objects.get(pk=request.data.get('user_id'))
            if user.role != "Counsellor":
                return Response(
                    {"error": "Only users with counsellor role can create profiles"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except MedicalHealthUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check for existing profile
        if hasattr(user, 'counsellor_profile'):
            return Response(
                {"error": "Profile already exists for this user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create profile
        serializer = CounsellorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateCounsellorProfile(APIView):
    permission_classes = []  # Add auth classes if needed

    def put(self, request, user_id):
        try:
            user = MedicalHealthUser.objects.get(pk=user_id)
            if not hasattr(user, 'counsellor_profile'):
                return Response({"error": "Profile does not exist"}, status=404)
        except MedicalHealthUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        profile = user.counsellor_profile

        serializer = CounsellorProfileUpdateSerializer(instance=profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Counsellor profile updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ListUsers(APIView):
    # authentication_classes = [JWTAuthentication]  # Use your custom JWTAuthentication
    # permission_classes = [IsAuthenticated]  # Optional: only allow logged-in users

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateUserView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'username': request.data.get('username', user.username),
            'email': request.data.get('email', user.email),
            'role': request.data.get('role', user.role)
        }

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "user": serializer.data,
                "is_active": user.is_active
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user

        if not user or not user.is_authenticated:
            raise NotAuthenticated('Authentication credentials were not provided or are invalid.')

        data = {
            'email': request.data.get('email', user.email),
            'username': request.data.get('username', user.username),
        }

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ToggleUserStatus(APIView):
    def put(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = not user.is_active  # toggle status
            user.save()
            status_str = "enabled" if user.is_active else "disabled"
            return Response({
                "message": f"User account has been {status_str}.",
                "user_id": user.id,
                "is_active": user.is_active
            }, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


class AdminByCreateUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if the requesting user is an admin
        if request.user.role != 'Admin':
            return Response({'error': 'Only admin users can perform this action'}, 
                          status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()  # Create mutable copy of request data
        
        # Set default role to 'View' if not provided
        if 'role' not in data:
            data['role'] = 'View'
        
        # Set username to email if username not provided
        if 'username' not in data and 'email' in data:
            data['username'] = data['email']

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            # Create user with verified status
            user = serializer.save()
            user.verified_at = now()  # Mark as verified immediately
            user.is_active = True     # Ensure user is active
            user.save()
            
            return Response({
                'message': 'User created successfully by admin',
                'user_id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'is_active': user.is_active,
                'verified_at': user.verified_at
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'User creation failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SendResetOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        otp = random.randint(100000, 999999)
        user.email_otp = otp
        user.verified_at = None  # Clear previous verification
        user.save()

        send_mail(
            'Password Reset OTP',
            f'Your OTP for resetting your password is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        return Response({'message': 'OTP sent to email'})
    

class VerifyResetOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if str(user.email_otp) != str(otp):
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        user.verified_at = now()
        user.email_otp = None  # Clear OTP after verification
        user.save()

        return Response({'message': 'OTP verified successfully'})


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if OTP was verified within last 10 minutes
        if not user.verified_at or now() - user.verified_at > timedelta(minutes=10):
            return Response({'error': 'OTP verification expired or not completed'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        # DO NOT clear verified_at here so the user can log in
        user.email_otp = None
        user.save()

        return Response({'message': 'Password reset successfully'})