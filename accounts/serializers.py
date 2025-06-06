from rest_framework import serializers
from .models import LANGUAGE_CHOICES, CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema_field

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Password must be at least 6 characters long."
    )
    preferred_language = serializers.ChoiceField(
        choices=LANGUAGE_CHOICES,
        required=False,
        default='en',
        help_text="Preferred language for communication (e.g., en, sw, yo, ig, and zu.)"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'preferred_language', 'password']
        extra_kwargs = {
            'email': {'help_text': 'User email address (will be used to log in).'},
            'first_name': {'help_text': 'User\'s first name.'},
            'last_name': {'help_text': 'User\'s last name.'},
            'phone_number': {'help_text': 'User\'s phone number (e.g., +234XXXXXXXXXX).'},
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = RefreshToken.for_user(user).access_token
        domain = get_current_site(self.context['request']).domain
        url = reverse('accounts:verify-email')
        link = f"http://{domain}{url}?token={token}"

        subject = 'Verify your email'
        message = f"Hi {user.get_full_name()},\n\nClick here to verify your email: {link}"

        send_mail(subject, message, None, [user.email])
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Email address to send the password reset link.")

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6,
        write_only=True,
        help_text="New password to set."
    )
    token = serializers.CharField(write_only=True, help_text="Token received in the password reset email.")
    uidb64 = serializers.CharField(write_only=True, help_text="User ID in base64 format.")

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Invalid or expired reset link")

            user.set_password(password)
            user.save()
            return user
        except Exception:
            raise serializers.ValidationError("Something went wrong. Please try again")
        


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, help_text="Current password.")
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        help_text="New password to set."
    )
    new_password_confirm = serializers.CharField(required=True, help_text="Repeat the new password to confirm.")

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "New passwords don't match."})
        return attrs
