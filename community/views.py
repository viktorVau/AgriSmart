# community/views.py

from rest_framework import generics, permissions
from .models import CommunityPost, Comment
from .serializers import CommunityPostSerializer, CommentSerializer
from .pagination import CommunityPagination
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(
    request=CommunityPostSerializer,
    responses={200: CommunityPostSerializer(many=True)},
    description=""
)
class CommunityPostListCreateView(generics.ListCreateAPIView):
    queryset = CommunityPost.objects.all().order_by('-created_at')
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommunityPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'body', 'author__first_name', 'author__last_name', 'author__email']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

@extend_schema(
    responses={200: CommunityPostSerializer},
    description="Retrieve, update, or delete a specific community post by ID."
)
class CommunityPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    request=CommentSerializer,
    responses={201: CommentSerializer},
    parameters=[
        OpenApiParameter(
            name='post_id',
            required=True,
            location=OpenApiParameter.PATH,
            description='ID of the Community Post to comment on.'
        )
    ],
    description="Create a new comment under a specific community post."
)
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = CommunityPost.objects.get(id=post_id)
        serializer.save(author=self.request.user, post=post)


# community/views.py
@extend_schema(
    description="CRUD operations on individual comments."
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiExample(
            'Helpful Toggled',
            value={"message": "Marked as helpful"}
        )},
        description="Toggle helpful mark for a comment by the current user."
    )
    @action(detail=True, methods=['post'], url_path='mark-helpful')
    def mark_helpful(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        if user in comment.helpful_by.all():
            comment.helpful_by.remove(user)
            return Response({"message": _("Removed from helpful")}, status=status.HTTP_200_OK)
        else:
            comment.helpful_by.add(user)
            return Response({"message": _("Marked as helpful")}, status=status.HTTP_200_OK)