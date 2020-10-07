from django.contrib import admin
from .models import Post, PostType
 
@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    ordering = ('type_name',)
    search_fields = ('type_name',)
 
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'p_type')
    ordering = ('title',)
    search_fields = ('title', 'p_type',)