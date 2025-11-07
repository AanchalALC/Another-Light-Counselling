from django.contrib import admin
from .models import (
    FAQ, Resource, Review, Contact, Member, Post, ContactDetails, Statistic,
    Service, DoIFeel, Policy, Committee, DynamicContent, PpcContact, Jd,
    OnboardingPlan, SpecializationTag, TeamPage
)

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

# --- NEW/UPDATED: Member admin ---
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name','pronouns','designation','availability','is_featured','order')
    list_filter  = ('availability','is_featured','keywords')
    search_fields = ('name','designation','languages')
    filter_horizontal = ('keywords',)  # <-- nicer UI for ManyToMany
    prepopulated_fields = {"slug": ("name",)}
    ordering = ('order','name')

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

@admin.register(Jd)
class JdAdmin(admin.ModelAdmin):
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

# --- NEW: Specialization tags for filters/chips ---
@admin.register(SpecializationTag)
class SpecializationTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

# --- NEW: Team Page singleton (hero/intro copy) ---
@admin.register(TeamPage)
class TeamPageAdmin(admin.ModelAdmin):
    list_display = ('hero_title',)
    # enforce single instance
    def has_add_permission(self, request):
        if TeamPage.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(OnboardingPlan)
class OnboardingPlanAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("tagline",)}
    list_display = ("tagline", "slug")
    ordering = ("slug",)
    search_fields = ("tagline", "slug")
