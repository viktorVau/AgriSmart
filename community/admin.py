from django.contrib import admin
from .models import Comment, CommunityPost

# Register your models here.
admin.site.register(Comment)
admin.site.register(CommunityPost)