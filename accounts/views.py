from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ChangePasswordSerializer, RegisterSerializer
from .models import CustomUser
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, force_bytes
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema



class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.
    Sends a verification email upon successful registration.
    """
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({'message': _('Check your email for verification')}, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    """
    Verify a user's email via token sent in email.
    """
    def get(self, request):
        token = request.GET.get('token')
        try:
            access_token = AccessToken(token)
            user = CustomUser.objects.get(id=access_token['user_id'])
            user.email_verified = True
            user.save()
            return redirect('/api/login/?verified=true')
        except Exception as e:
            return Response({'error': _('Invalid or expired token')}, status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetEmail(generics.GenericAPIView):
    """
    Request a password reset email by providing your account email.
    """
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        email = request.data.get('email', '')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            relative_link = reverse('accounts:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            abs_url = f"http://localhost:8000{relative_link}"
            email_body =  _(f"Hi {user.get_full_name()},\nUse the link below to reset your password:\n{abs_url}")
            email = EmailMessage(subject="Reset Your Password", body=email_body, to=[user.email])
            email.send()
        return Response({"message": _("If your email is in our system, we have sent you a link to reset your password.")}, status=status.HTTP_200_OK)

class PasswordTokenCheckAPI(generics.GenericAPIView):
    """
    Validate the token and UID from password reset email.
    """
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"error": _("Token is invalid or expired")}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"success": True, "uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": _("Token is invalid or expired")}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordAPIView(generics.GenericAPIView):
    """
    Set a new password after verifying the reset token and UID.
    """
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": _("Password reset successful!")}, status=status.HTTP_200_OK)
    
class ChangePasswordView(APIView):
    """
    Change password for an authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": _("Incorrect password.")}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"success": _("Password changed successfully.")}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

User = get_user_model()

class DeactivateAccountView(APIView):
    """
    Allows a logged-in user to deactivate their own account (soft delete).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        user = request.user

        if not password:
            return Response({'error': _('Password is required.')}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the password is correct
        if not user.check_password(password):
            return Response({'error': _('Invalid password.')}, status=status.HTTP_400_BAD_REQUEST)

        # Deactivate the account
        user.is_active = False
        user.save()

        return Response({'message': _('Account deactivated successfully.')}, status=status.HTTP_200_OK)


class ReactivateAccountView(APIView):
    """
    Allows a user to reactivate their deactivated account using their email and password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': _('Email and password are required.')}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({'detail': _('Invalid credentials or account does not exist.')}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({'detail': _('Account is already active.')}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'detail': _('Account reactivated successfully.'),
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
