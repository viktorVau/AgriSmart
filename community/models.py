from django.db import models

# Create your models here.
# community/models.py
from django.conf import settings

class CommunityPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(CommunityPost, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    helpful_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='helpful_comments', blank=True)

    def helpful_count(self):
        return self.helpful_by.count()

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"