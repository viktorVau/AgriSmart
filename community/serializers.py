# community/serializers.py

from rest_framework import serializers
from .models import CommunityPost, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    helpful_count = serializers.IntegerField(read_only=True)
    is_helpful_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_name', 'body', 'created_at', 'helpful_count', 'is_helpful_by_me']
        read_only_fields = ['id', 'author', 'author_name', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.email

    def get_is_helpful_by_me(self, obj):
        user = self.context['request'].user
        return user in obj.helpful_by.all()
    

class CommunityPostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = CommunityPost
        fields = ['id', 'author', 'author_name', 'title', 'body', 'created_at', 'comments']
        read_only_fields = ['id', 'author', 'author_name', 'created_at', 'comments']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.email
