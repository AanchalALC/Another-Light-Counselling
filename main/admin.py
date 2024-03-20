from django.contrib import admin
from .models import FAQ, Resource, Review, Contact, Member, Post, ContactDetails, Statistic, Service, DoIFeel,NewCategory, Policy, Committee, DynamicContent, PpcContact
 
# @admin.register(PostType)
# class PostTypeAdmin(admin.ModelAdmin):
#     list_display = ('type_name',)
#     ordering = ('type_name',)
#     search_fields = ('type_name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    exclude = ('site',)
    list_display = ('title',)
    ordering = ('id',)
    search_fields = ('title',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    exclude = ('site',)
    list_display = ('question',)
    ordering = ('id',)
    search_fields = ('question',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    exclude = ('site',)
    ordering = ('id',)
    search_fields = ('review',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    exclude = ('site',)
    ordering = ('name',)
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    exclude = ('site',)
    ordering = ('name', 'id', )
    search_fields = ('name', 'number', 'instahandle',)

@admin.register(PpcContact)
class PpcContactAdmin(admin.ModelAdmin):
    exclude = ('site',)
    ordering = ('name', 'id', )
    search_fields = ('name', 'email', 'contact',)

@admin.register(ContactDetails)
class ContactDetailsAdmin(admin.ModelAdmin):
    list_display = ('title', 'value',)
    ordering = ('title',)
    search_fields = ('title', 'value',)

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('name', 'value',)
    ordering = ('name', 'value',)
    search_fields = ('name', )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title', )


@admin.register(DoIFeel)
class DoIFeelAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title', )
    
@admin.register(NewCategory)
class NewCategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title', )

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title', )

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title', )

@admin.register(DynamicContent)
class DynamicContentAdmin(admin.ModelAdmin):
    list_display = ('key', 'title',)
    ordering = ('key',)
    search_fields = ('key', 'title', )