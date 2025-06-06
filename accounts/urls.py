from django.urls import path
from .views import ChangePasswordView, DeactivateAccountView, PasswordTokenCheckAPI, ReactivateAccountView, RegisterView, RequestPasswordResetEmail, SetNewPasswordAPIView, VerifyEmailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('deactivate-account/', DeactivateAccountView.as_view(), name='deactivate-account'),
    path('reactivate-account/', ReactivateAccountView.as_view(), name='reactivate-account'),
]
