from django.urls import path
from .views import CropPredictionView, CustomTokenObtainPairView, FarmerListView, FarmerRegisterView, AgronomistRegisterView, ManualSoilTestView, MeView, SoilImageAnalysisView, WeatherForecastView, WeatherView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('farmers-register/', FarmerRegisterView.as_view(), name='farmers-register'),
    path('farmers-login/', CustomTokenObtainPairView.as_view(), name='farmers-login'),
    path('agronomists-register/', AgronomistRegisterView.as_view(), name='agronomists-register'),
    path('agronomists-login/', CustomTokenObtainPairView.as_view(), name='agronomists-login'),
    path('farmers/', FarmerListView.as_view(), name='farmer-list'),
    path('me/', MeView.as_view(), name='me-view'),
    path('weather/', WeatherView.as_view(), name='weather'),
    path("weather/forecast/", WeatherForecastView.as_view(), name="weather-forecast"),
    path('predict-crop/', CropPredictionView.as_view(), name='predict-crop'),
    path('soil-test/manual/', ManualSoilTestView.as_view(), name='manual-soil-test'),
    path('soil-test/image/', SoilImageAnalysisView.as_view(), name='soil-image-analysis'),
]
