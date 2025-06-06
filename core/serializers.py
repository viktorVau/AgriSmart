from rest_framework import serializers
from accounts.models import CustomUser
from .models import Farmer, Agronomist, SoilTest
from accounts.serializers import RegisterSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class BaseProfileRegisterSerializer(serializers.ModelSerializer):
    user = RegisterSerializer(help_text="User credentials and personal info (email, name, phone, password)")
    profile_image = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Optional profile picture"
    )

    class Meta:
        abstract = True
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        request = self.context.get('request')
        user_serializer = RegisterSerializer(data=user_data, context={'request': request})
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        return self.Meta.model.objects.create(user=user, **validated_data)


class FarmerRegisterSerializer(BaseProfileRegisterSerializer):
    class Meta(BaseProfileRegisterSerializer.Meta):
        model = Farmer
        fields = '__all__'
        extra_kwargs = {
            'location': {'help_text': 'City, village, or GPS location of the farm'},
            'farm_size': {'help_text': 'Size of the farm in hectares'},
        }


class FarmerListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', help_text="Farmer's first name")
    last_name = serializers.CharField(source='user.last_name', help_text="Farmer's last name")

    class Meta:
        model = Farmer
        fields = ['id', 'first_name', 'last_name', 'location', 'farm_size', 'profile_image']


class AgronomistRegisterSerializer(BaseProfileRegisterSerializer):
    class Meta(BaseProfileRegisterSerializer.Meta):
        model = Agronomist
        fields = '__all__'
        extra_kwargs = {
            'profile_image': {'help_text': 'Optional profile image for the agronomist'},
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['email'] = self.user.email

        if hasattr(self.user, 'farmer'):
            data['role'] = 'farmer'
        elif hasattr(self.user, 'agronomist'):
            data['role'] = 'agronomist'
        else:
            data['role'] = 'unknown'
        return data


class SoilTestSerializer(serializers.ModelSerializer):
    ph = serializers.FloatField(help_text="Soil pH value (acidity/alkalinity)")
    nitrogen = serializers.FloatField(help_text="Nitrogen content (N) in mg/kg")
    phosphorus = serializers.FloatField(help_text="Phosphorus content (P) in mg/kg")
    potassium = serializers.FloatField(help_text="Potassium content (K) in mg/kg")

    class Meta:
        model = SoilTest
        fields = ['ph', 'nitrogen', 'phosphorus', 'potassium']


class SoilImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(help_text="Upload a photo of soil for analysis")
