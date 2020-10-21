from django.contrib import admin
from .models import Post, PostType, FAQ, Resource
 
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

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('id',)
    search_fields = ('title',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question',)
    ordering = ('id',)
    search_fields = ('question',)