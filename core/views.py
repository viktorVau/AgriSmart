from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from .serializers import CustomTokenObtainPairSerializer, FarmerListSerializer, FarmerRegisterSerializer, AgronomistRegisterSerializer, SoilTestSerializer
from .models import Agronomist, Farmer, SoilTest
from .filters import FarmerFilter
from .pagination import FarmerPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from .weather import get_forecast_average_by_city, get_forecast_by_city, get_weather_by_city
from .predict import recommend_crop
from .serializers import SoilImageUploadSerializer
from .soil_analysis import analyze_soil_image
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from django.shortcuts import redirect
from django.views import View

class RootRedirectView(View):
    def get(self, request, *args, **kwargs):
        return redirect('/admin/')


@extend_schema(
    request=FarmerRegisterSerializer,
    responses={201: OpenApiExample('Farmer created', value={"message": "Farmer account created. Please check your email to verify your account."})},
    description="Register a new farmer. Sends email verification.")
class FarmerRegisterView(generics.CreateAPIView):
    serializer_class = FarmerRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": _("Farmer account created. Please check your email to verify your account.")}, status=status.HTTP_201_CREATED)


@extend_schema(
    request=AgronomistRegisterSerializer,
    responses={201: OpenApiExample('Agronomist created', value={"message": "Agronomist account created. Please check your email to verify your account."})},
    description="Register a new agronomist. Sends email verification."
)
class AgronomistRegisterView(generics.CreateAPIView):
    serializer_class = AgronomistRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": _("Agronomist account created. Please check your email to verify your account.")}, status=status.HTTP_201_CREATED)
    
@extend_schema(
    description="List all farmers. Requires authentication. Supports filtering and pagination.",
    responses=FarmerListSerializer(many=True)
)
class FarmerListView(generics.ListAPIView):
    queryset = Farmer.objects.select_related('user').all().order_by('-created_at')
    serializer_class = FarmerListSerializer
    pagination_class = FarmerPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = FarmerFilter
    permission_classes = [IsAuthenticated]


@extend_schema(
    methods=["GET"],
    responses={
        200: OpenApiResponse(
            response=None,
            description="Authenticated profile (Farmer or Agronomist)",
            examples=[
                OpenApiExample(
                    name="Farmer example",
                    value={"first_name": "John", "farm_name": "Green Acres"},
                    response_only=True
                ),
                OpenApiExample(
                    name="Agronomist example",
                    value={"first_name": "Jane", "specialty": "Soil Health"},
                    response_only=True
                )
            ]
        )
    },
    description="Get the authenticated user's profile (Farmer or Agronomist)."
)
@extend_schema(
    methods=["PATCH"],
    request=FarmerRegisterSerializer,  # You can't combine serializers here; use a common serializer or custom one
    responses={200: FarmerRegisterSerializer},  # Same limitation
    description="Update the authenticated user's profile."
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object_and_serializer(self, user):
        try:
            farmer = Farmer.objects.get(user=user)
            return farmer, FarmerRegisterSerializer
        except Farmer.DoesNotExist:
            pass

        try:
            agronomist = Agronomist.objects.get(user=user)
            return agronomist, AgronomistRegisterSerializer
        except Agronomist.DoesNotExist:
            pass

        return None, None

    def get(self, request):
        profile, serializer_class = self.get_object_and_serializer(request.user)
        if profile:
            serializer = serializer_class(profile)
            return Response(serializer.data)
        return Response({"detail": _("Profile not found.")}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        profile, serializer_class = self.get_object_and_serializer(request.user)
        if not profile:
            return Response({"detail": _("Profile not found.")}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializer_class(profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

@extend_schema(
    request=CustomTokenObtainPairSerializer,
    responses={200: CustomTokenObtainPairSerializer},
    description="JWT login with role included in response."
)    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(
    parameters=[OpenApiParameter(name="city", required=False, description="City name (optional if user is a farmer)")],
    description="Get current weather data for a city or the farmer's location."
)
class WeatherView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = request.query_params.get("city")

        if not city:
            try:
                farmer = Farmer.objects.get(user=request.user)
                city = farmer.location
            except Farmer.DoesNotExist:
                return Response({"error": _("City not provided and no location found for user.")}, status=400)

        weather_data = get_weather_by_city(city)
        return Response(weather_data)
    

@extend_schema(
    parameters=[OpenApiParameter(name="city", required=False, description="City name (optional if user is a farmer)")],
    description="Get 5-day weather forecast for a city or the farmer's location."
)
class WeatherForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = request.query_params.get("city")

        if not city:
            try:
                farmer = Farmer.objects.get(user=request.user)
                city = farmer.location
            except Farmer.DoesNotExist:
                return Response({"error": _("City not provided and no location found for user.")}, status=400)

        forecast_data = get_forecast_by_city(city)
        return Response(forecast_data)
    

@extend_schema(
    request=OpenApiExample(
        'Prediction input',
        value={
            "N": 90, "P": 42, "K": 43, "ph": 6.5,
            "temperature": 28, "humidity": 60, "rainfall": 150,
            "forecast": "false", "city": "Nairobi"
        }
    ),
    description="Predict suitable crops using soil and optional weather data.",
    responses={200: OpenApiExample(
        'Prediction Result',
        value={"recommended_crops": [{"crop": "maize", "confidence": "95%"}]}
    )}
)
class CropPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        base_fields = ['N', 'P', 'K', 'ph']
        missing_fields = [field for field in base_fields if field not in request.data]
        if missing_fields:
            return Response({"error": _(f"Missing required fields: {', '.join(missing_fields)}.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = {field: float(request.data[field]) for field in base_fields}

            # Weather data (manual input or fetched)
            temperature = request.data.get('temperature')
            humidity = request.data.get('humidity')
            rainfall = request.data.get('rainfall')

            use_forecast = request.data.get('forecast', 'false').lower() == 'true'

            if temperature and humidity and rainfall:
                data['temperature'] = float(temperature)
                data['humidity'] = float(humidity)
                data['rainfall'] = float(rainfall)
                forecast_used = False
            else:
                city = request.data.get('city')
                if not city:
                    try:
                        farmer = Farmer.objects.get(user=request.user)
                        city = farmer.location
                    except Farmer.DoesNotExist:
                        return Response({"error": _("Weather info missing and no city provided or found in profile.")}, status=400)

                if use_forecast:
                    weather_data = get_forecast_average_by_city(city)
                    forecast_used = True
                else:
                    weather_data = get_weather_by_city(city)
                    forecast_used = False

                if weather_data.get("error"):
                    return Response({"error": weather_data["error"]}, status=500)

                data['temperature'] = weather_data['temperature']
                data['humidity'] = weather_data['humidity']
                data['rainfall'] = weather_data['rainfall']

            recommend = recommend_crop(data)
            return Response({
                "recommended_crops": [
                    {"crop": _(crop), _("confidence"): f"{confidence}%"}
                    for crop, confidence in recommend
                ],
                "used_data": data,
                "forecast_used": forecast_used
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@extend_schema(
    request=SoilTestSerializer,
    responses={200: OpenApiExample('Success', value={"message": "Soil test submitted", "recommendation": "Add lime."})},
    description="Submit a manual soil test and get basic pH recommendations."
)
class ManualSoilTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SoilTestSerializer(data=request.data)
        if serializer.is_valid():
            # Save the test (optional)
            SoilTest.objects.create(user=request.user, **serializer.validated_data)
            
            # Dummy analysis logic (you can replace with real thresholds or ML logic)
            ph = serializer.validated_data['ph']
            nitrogen = serializer.validated_data['nitrogen']
            phosphorus = serializer.validated_data['phosphorus']
            potassium = serializer.validated_data['potassium']

            if ph < 5.5:
                recommendation = _("Soil is too acidic. Consider adding lime.")
            elif ph > 7.5:
                recommendation = _("Soil is too alkaline. Consider adding sulfur.")
            else:
                recommendation = _("pH level is optimal.")

            return Response({
                "message": _("Soil test submitted successfully."),
                "recommendation": _(recommendation)},
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@extend_schema(
    request=SoilImageUploadSerializer,
    responses={200: OpenApiExample('Analysis result', value={"result": "Soil appears healthy."})},
    description="Upload an image for AI-based soil analysis."
)
class SoilImageAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SoilImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            result = analyze_soil_image(image)
            return Response({
                "message": _("Soil image analyzed successfully."),
                "result": result
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)