import jwt
from django.conf import settings
from django.utils import translation
from accounts.models import CustomUser  # adjust if needed


class LanguagePreferenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = None
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if token:
            try:
                # Decode the JWT token manually
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded.get('user_id')
                user = CustomUser.objects.get(id=user_id)
                lang = user.preferred_language or 'en'
                print(f"[Middleware] JWT user: {user.email}, Language: {lang}")
                translation.activate(lang)
            except Exception as e:
                print(f"[Middleware] JWT decode failed: {e}")
                translation.activate('en')
        else:
            print("[Middleware] No JWT token. Defaulting to English.")
            translation.activate('en')

        response = self.get_response(request)
        translation.deactivate()
        return response
