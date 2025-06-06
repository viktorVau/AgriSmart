from rest_framework.pagination import PageNumberPagination

class FarmerPagination(PageNumberPagination):
    page_size = 10  # Adjust based on frontend layout (e.g., 8 or 12 for card grids)
    page_size_query_param = 'page_size'
    max_page_size = 100
