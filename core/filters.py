import django_filters
from .models import Farmer

class FarmerFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(field_name='user__first_name', lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    is_verified = django_filters.BooleanFilter(field_name='user__email_verified')

    class Meta:
        model = Farmer
        fields = ['first_name', 'location', 'is_verified']
