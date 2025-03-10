import random
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.conf import settings
import jwt

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
        print(data)
        email = data.get('email')

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

                return Response({'message': 'OTP sent to your email', 'user_id': user.id}, status=status.HTTP_200_OK)

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

        return Response({
            'message': 'Login successful',
            'token': token,
            'user': user_data
        }, status=status.HTTP_200_OK)