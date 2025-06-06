# community/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunityPostListCreateView,
    CommunityPostDetailView,
    CommentCreateView,
    CommentViewSet,
)

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('posts/', CommunityPostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', CommunityPostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
    path('', include(router.urls)), 
]