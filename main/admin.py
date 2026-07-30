from django.contrib import admin
from .models import (
    FAQ, Resource, Review, Contact, Member, Post, ContactDetails, Statistic,
    Service, DoIFeel, Policy, Committee, DynamicContent, PpcContact, Jd,
    OnboardingPlan, SpecializationTag, TeamPage,  MemberBlogPost, MediaFeature,
    GoogleReview, GoogleReviewStats
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
    
@admin.register(GoogleReview)
class GoogleReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'rating', 'short_comment', 'source',
                    'is_published', 'is_pinned', 'created_at_google')
    list_editable = ('is_published', 'is_pinned')
    list_filter = ('is_published', 'is_pinned', 'rating', 'source')
    search_fields = ('author_name', 'comment', 'reply_comment')
    ordering = ('-is_pinned', '-created_at_google', '-id')
    date_hierarchy = 'created_at_google'
    exclude = ('site',)
    actions = ('publish', 'unpublish')

    # Everything except the moderation toggles belongs to Google. Editing it by
    # hand just gets overwritten on the next sync, so it is locked.
    readonly_fields = (
        'source', 'external_id', 'author_name', 'author_photo_url', 'rating',
        'comment', 'review_url', 'created_at_google', 'updated_at_google',
        'reply_comment', 'reply_time', 'synced_at',
    )

    def short_comment(self, obj):
        text = (obj.comment or '').replace('\n', ' ')
        return (text[:80] + '...') if len(text) > 80 else (text or '(rating only)')
    short_comment.short_description = 'Review'

    def publish(self, request, queryset):
        self.message_user(request, '%d review(s) published.' % queryset.update(is_published=True))
    publish.short_description = 'Publish selected reviews'

    def unpublish(self, request, queryset):
        self.message_user(request, '%d review(s) hidden.' % queryset.update(is_published=False))
    unpublish.short_description = 'Hide selected reviews from the site'

    def has_add_permission(self, request):
        # Reviews arrive via sync_google_reviews / import_reviews_csv only.
        return False


@admin.register(GoogleReviewStats)
class GoogleReviewStatsAdmin(admin.ModelAdmin):
    list_display = ('average_rating', 'total_ratings', 'last_synced', 'last_status')
    readonly_fields = ('average_rating', 'total_ratings', 'reviews_url',
                       'write_review_url', 'last_synced', 'last_status')
    exclude = ('site',)

    def has_add_permission(self, request):
        return not GoogleReviewStats.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
