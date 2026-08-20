from django.contrib import admin
from .models import (
    FAQ, Resource, Review, Contact, Member, Post, ContactDetails, Statistic,
    Service, ServiceFAQ, ServicesHubPage, DoIFeel, Policy, Committee, DynamicContent, PpcContact, Jd,
    OnboardingPlan, SpecializationTag, TeamPage,  MemberBlogPost, MediaFeature
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
    list_display = ('question', 'show_on_services_hub')
    list_filter = ('show_on_services_hub',)
    list_editable = ('show_on_services_hub',)
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
    list_display = ('name','pronouns','designation','availability','is_featured','order', "is_therapist")
    list_filter  = ('availability','is_featured','keywords',"is_therapist" )
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

class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 1
    fields = ('question', 'answer', 'order')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published')
    list_filter = ('category', 'is_published')
    list_editable = ('is_published',)
    ordering = ('category', 'title')
    search_fields = ('title', )
    inlines = [ServiceFAQInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'is_published', 'image_file', 'img_alt_text'),
        }),
        ('Intro (existing content — unchanged)', {
            'fields': ('content',),
        }),
        ('Detail page sections (optional — leave blank to hide)', {
            'fields': (
                'hero_subtitle', 'short_summary', 'who_its_for', 'how_it_works',
                'session_looks_like', 'format_availability', 'credibility_blurb',
            ),
        }),
        ('Booking CTA', {
            'fields': ('cta_whatsapp_message',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
        }),
    )

@admin.register(ServicesHubPage)
class ServicesHubPageAdmin(admin.ModelAdmin):
    list_display = ('hub_heading', 'video_source')
    fieldsets = (
        ('Hero', {
            'fields': ('hub_heading', 'hub_intro'),
        }),
        ('Why Choose Another Light Counselling? (leave points blank to hide the section)', {
            'fields': ('why_choose_intro', 'why_choose_points'),
        }),
        ('Our Therapy Process (leave a step title blank to stop before that step)', {
            'fields': (
                'process_step1_title', 'process_step1_detail',
                'process_step2_title', 'process_step2_detail',
                'process_step3_title', 'process_step3_detail',
                'process_step4_title', 'process_step4_detail',
            ),
        }),
        ('Video slot', {
            'fields': ('video_source', 'video_file', 'video_youtube_url', 'video_poster', 'video_caption'),
        }),
    )
    def has_add_permission(self, request):
        if ServicesHubPage.objects.exists():
            return False
        return super().has_add_permission(request)

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

@admin.register(MemberBlogPost)
class MemberBlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "member", "is_published", "published_at")
    list_filter = ("is_published", "member")
    search_fields = ("title", "member__name", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at", "-id")
    
@admin.register(MediaFeature)
class MediaFeatureAdmin(admin.ModelAdmin):
    exclude = ('site',)
    list_display = ('outlet_name', 'feature_type', 'article_title', 'order', 'is_active')
    list_editable = ('feature_type', 'order', 'is_active')
    list_filter = ('feature_type', 'is_active')
    search_fields = ('outlet_name', 'article_title', 'kicker', 'description')
    ordering = ('feature_type', 'order', 'id')
    fieldsets = (
        (None, {
            'fields': ('feature_type', 'outlet_name', 'order', 'is_active'),
        }),
        ('Logo (for logo carousel & article cards)', {
            'fields': ('logo', 'logo_alt'),
        }),
        ('Article / More features', {
            'fields': ('kicker', 'article_title', 'description', 'link'),
        }),
        ('Video highlight', {
            'fields': ('video_url',),
        }),
    )