from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.sites.models import Site
from ckeditor_uploader.fields import RichTextUploadingField


class PostType(models.Model):
    type_name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.type_name)


class FAQ(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    question = models.CharField(max_length=500)
    answer = RichTextUploadingField()
    show_on_services_hub = models.BooleanField(
        default=False,
        help_text="Tick to also feature this FAQ (with FAQPage schema) on the Services hub page. "
                   "Keep the hub selection to 4-6 highly relevant questions."
    )
    tippy_answer = ''

    def generate_tooltip_markup(self):
        self.tippy_answer = self.answer
        tooltips = [
            'depression',
            'dissociation',
            'anxiety',
            'addiction',
            'gender',
            'sexuality',
            'trauma'
        ]
        for word in tooltips:
            self.tippy_answer = str(self.tippy_answer).replace(
                word,
                '<span class="mytooltip {word}tippy">{word}</span>'.format(word=word)
            )

    def __str__(self):
        return str(self.question)


class Resource(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=500)
    thumbnail = models.ImageField(upload_to='resources')
    link = models.CharField(max_length=1000)


# --------- NEW: Specialization tags (e.g., Trauma, DBT) ---------
class SpecializationTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, blank=True, default="")  # optional HEX for chips

    def __str__(self):
        return self.name
    class Meta:
        ordering = ('name',)


# --------- UPDATED: Member (backwards-compatible) ---------
class Member(models.Model):
    # --- Listing / legacy fields ---
    thumbnail    = models.ImageField(upload_to='members')
    name         = models.CharField(max_length=700)
    designation  = models.CharField(max_length=700)
    info         = RichTextUploadingField()  # legacy long bio; kept for compatibility
    order        = models.IntegerField(default=1)
    img_alt      = models.CharField(max_length=400, blank=True, default='')

    # --- Routing & identity ---
    slug         = models.SlugField(max_length=120, unique=True, blank=True)
    pronouns     = models.CharField(max_length=60, blank=True, default='')

    # --- Profile assets/sections ---
    profile_image   = models.ImageField(upload_to='members', blank=True)     # hero/profile image
    short_bio       = models.TextField(blank=True, default='')               # for cards/previews
    bio_long        = RichTextUploadingField(blank=True, default='')         # full intro (can copy from info)
    intro_video_url = models.URLField(blank=True, default='')                # raw YouTube URL
    
    is_therapist = models.BooleanField(
        default=True,
        help_text="Tick for anyone who actually does therapy sessions."
    )

    AVAILABILITY_CHOICES = [
        ('open', 'Accepting new clients'),
        ('waitlist', 'Waitlist only'),
        ('unavailable', 'Not taking clients'),
    ]
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        blank=True,
        null=True,
        default=''
    )

    # --- Taxonomy & qualifications ---
    keywords       = models.ManyToManyField('SpecializationTag', blank=True, related_name='members')
    certifications = RichTextUploadingField(blank=True, default='')

    # --- CTAs/links ---
    blog_url    = models.URLField(blank=True, default='')
    media_url   = models.URLField(blank=True, default='')   # interviews/reels
    booking_url = models.URLField(blank=True, default='')   # WhatsApp/Exly/etc.
    languages   = models.CharField(max_length=200, blank=True, default='')  # e.g., "English, Hindi"
    is_featured = models.BooleanField(default=False)

    # --- Helper (not a DB field) ---
    layout_position = ''  # used only for alternating layout in old templates

    # -------- Legacy tooltip generator (kept) --------
    def generate_tooltip_markup(self):
        self.tippy_info = self.info
        for word in ['depression', 'dissociation', 'anxiety', 'addiction', 'gender', 'sexuality', 'trauma']:
            self.tippy_info = str(self.tippy_info).replace(
                word, f'<span class="mytooltip {word}tippy">{word}</span>'
            )

    # -------- Routing & helpers --------
    def _unique_slug(self, base):
        base = (slugify(base).replace('-', '') or 'member')[:110]
        slug_candidate = base
        n = 2
        Model = self.__class__
        while Model.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
            slug_candidate = f"{base}-{n}"
            n += 1
        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.name or f"member-{self.pk or ''}"
            self.slug = self._unique_slug(base)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # safe fallback avoids NoReverseMatch if slug ever missing
        if not self.slug:
            return reverse('about')
        return reverse('member-profile', args=[self.slug])

    def youtube_embed_url(self):
        """Return an embeddable YouTube URL or empty string."""
        if not self.intro_video_url:
            return ''
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.intro_video_url)
        video_id = ''
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/')
        elif 'youtube.com' in parsed.netloc:
            video_id = parse_qs(parsed.query).get('v', [''])[0]
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1" if video_id else ''

    def primary_image_url(self):
        """Convenience for templates: prefer profile_image, else thumbnail."""
        if self.profile_image:
            return self.profile_image.url
        return self.thumbnail.url if self.thumbnail else ''

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('order', 'name')

class MemberBlogPost(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="blog_posts"
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=160, blank=True)

    cover_image = models.ImageField(
        upload_to="member_blogs/covers",
        blank=True,
        null=True
    )

    excerpt = models.TextField(blank=True, default="")
    body = RichTextUploadingField()

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now=True)

    # Optional SEO (keeps parity with Post/Service patterns)
    meta_title = models.CharField(max_length=250, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    meta_keywords = models.CharField(max_length=500, blank=True, default="")

    def __str__(self):
        return f"{self.member.name} — {self.title}"

    def get_absolute_url(self):
        return reverse("member-blog-detail", args=[self.member.slug, self.slug])

    def save(self, *args, **kwargs):
        # slug
        if not self.slug:
            self.slug = slugify(self.title)[:155]

        # published_at
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        # SEO defaults
        if not self.meta_title:
            self.meta_title = self.title

        if not self.meta_description:
            # lightweight preview from excerpt if present, else from body
            base = self.excerpt.strip() if self.excerpt else str(self.body)
            # reuse your existing preview helper style (simple + safe)
            try:
                first_para = str(base).split('</p>')[0].split('<p>')[1]
                words = first_para.split(' ')[:35]
                if words and words[-1].endswith(','):
                    words[-1] = words[-1][:-1]
                self.meta_description = ' '.join(words) + '...'
            except Exception:
                self.meta_description = (base[:160] + '...') if len(base) > 160 else base

        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("-published_at", "-id")
        constraints = [
            models.UniqueConstraint(fields=["member", "slug"], name="uniq_member_blog_slug")
        ]
        verbose_name = "Therapist Blog Post"
        verbose_name_plural = "Therapist Blog Posts"

class Review(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    review = models.TextField()

    def get_preview(self):
        return ' '.join(str(self.review).split(' ')[:15]) + '...'

    def __str__(self):
        return self.get_preview()


class Contact(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=500)
    number = models.CharField(max_length=20)
    instahandle = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        name = str(self.name)
        number = str(self.number)
        return name if len(name) > 0 else number

    class Meta:
        verbose_name = 'Person Who Reached Out'
        verbose_name_plural = 'People Who Reached Out'


class PpcContact(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=500)
    email = models.CharField(max_length=60, null=True, blank=True)
    contact = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        name = str(self.name)
        email = str(self.email)
        return name if len(name) > 0 else email

    class Meta:
        verbose_name = 'PPC Lead'
        verbose_name_plural = 'PPC Leads'


class ContactDetails(models.Model):
    key = models.CharField(max_length=250, verbose_name="Key (Do Not Change)")
    symbol = models.CharField(max_length=250, verbose_name="Symbol (font-awesome)")
    title = models.CharField(max_length=250)
    value = models.CharField(max_length=250)
    url = models.CharField(max_length=400, default="")

    def __str__(self):
        name = str(self.title)
        val = str(self.value)
        return f'{name}: {val}'

    class Meta:
        verbose_name = 'Another Light Contact Detail'
        verbose_name_plural = 'Another Light Contact Details'


class Statistic(models.Model):
    name = models.CharField(max_length=250)
    value = models.IntegerField(default=0)

    def __str__(self):
        name = str(self.name)
        val = str(self.value)
        return f'{name}: {val}'

    class Meta:
        verbose_name = 'Statistic'
        verbose_name_plural = 'Statistics'


class Service(models.Model):
    # Taxonomy per the ALC services-page brief (servicepage-suggestion-ALC.pdf).
    CATEGORY_TRAUMA = 'trauma-recovery'
    CATEGORY_MENTAL_HEALTH = 'mental-health-wellbeing'
    CATEGORY_RELATIONSHIPS = 'relationship-couples'
    CATEGORY_IDENTITY = 'gender-identity'
    CATEGORY_CHOICES = [
        (CATEGORY_TRAUMA, 'Trauma Recovery & Healing Therapies'),
        (CATEGORY_MENTAL_HEALTH, 'Individual Mental Health & Emotional Wellbeing'),
        (CATEGORY_RELATIONSHIPS, 'Relationship & Couples Counselling'),
        (CATEGORY_IDENTITY, 'Gender, Sexuality & Identity Affirming Therapy'),
    ]
    # Fixed display order for the hub/nav grouping; categories not listed here sort last.
    CATEGORY_ORDER = [
        CATEGORY_TRAUMA,
        CATEGORY_MENTAL_HEALTH,
        CATEGORY_RELATIONSHIPS,
        CATEGORY_IDENTITY,
    ]

    # Deterministic palette theme per service (hash of slug -> one of 5 brand colors).
    # Mirrors the client-side theme array already used on doifeel.html, but computed
    # server-side so there's no JS randomisation and no flash-of-unstyled-color.
    CARD_THEMES = [
        {'bg': '#F08C21', 'text': '#FFFFFF', 'light': False},  # Tangerine
        {'bg': '#F2D88F', 'text': '#2C2C2C', 'light': True},   # Butter
        {'bg': '#E36888', 'text': '#FFFFFF', 'light': False},  # Blush
        {'bg': '#6698CC', 'text': '#FFFFFF', 'light': False},  # Sea
        {'bg': '#B4B534', 'text': '#2C4A22', 'light': True},   # Matcha
    ]

    image_file = models.ImageField(upload_to='services', blank=True)
    title = models.CharField(max_length=250)
    img_alt_text = models.CharField(max_length=250, blank=True, default='')
    content = RichTextUploadingField()
    slug = models.SlugField(max_length=100, blank=True)
    # SEO FIELDS
    meta_title = models.CharField(max_length=250, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.CharField(max_length=500, blank=True, default='')

    # PUBLISHING
    is_published = models.BooleanField(
        default=True,
        help_text="Untick to hide this service everywhere (nav, hub, sitemap, direct URL) "
                   "without deleting it. New services default to this being off until you're ready to go live."
    )

    # CATEGORY (for the services hub + nav grouping + related modalities)
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, blank=True, default='',
        help_text="Which group this service appears under on the Services hub and nav dropdown."
    )

    # STRUCTURED DETAIL-PAGE SECTIONS (all optional — leave blank and the section just won't show)
    hero_subtitle = models.CharField(
        max_length=300, blank=True, default='',
        help_text="One short line under the page title, e.g. 'Support for processing traumatic experiences at your own pace.'"
    )
    short_summary = models.CharField(
        max_length=400, blank=True, default='',
        help_text="25-40 word summary shown on the Services hub card grid. Leave blank and the hero subtitle is used instead."
    )
    who_its_for = RichTextUploadingField(
        blank=True, default='',
        help_text="'Who this is for' section — signs/symptoms that suggest this service is a fit."
    )
    how_it_works = RichTextUploadingField(
        blank=True, default='',
        help_text="'How it works at ALC' — process, safety, pacing."
    )
    session_looks_like = RichTextUploadingField(
        blank=True, default='',
        help_text="'What a session looks like' — practical, concrete expectations."
    )
    format_availability = RichTextUploadingField(
        blank=True, default='',
        help_text="Format & availability — e.g. online globally / in-person Mumbai (Andheri + 180 Studio Bandra)."
    )
    credibility_blurb = RichTextUploadingField(
        blank=True, default='',
        help_text="Optional short note above the therapist/supervision credibility block. Leave blank for the standard text."
    )
    cta_whatsapp_message = models.CharField(
        max_length=300, blank=True, default='',
        help_text="Optional pre-filled WhatsApp message for this service's booking CTA. "
                   "Leave blank to use the site-wide default message."
    )

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('service', args=[self.slug])

    def _theme(self):
        import zlib
        index = zlib.crc32(self.slug.encode('utf-8')) % len(self.CARD_THEMES)
        return self.CARD_THEMES[index]

    def card_color(self):
        """Deterministic brand-palette colour for hub/nav cards, derived from the slug."""
        return self._theme()['bg']

    def card_text_color(self):
        """Readable text colour for whatever card_color() picked (white on dark, ink on light)."""
        return self._theme()['text']

    def card_theme_is_light(self):
        return self._theme()['light']

    def card_summary(self):
        """25-40 word hub-card summary, falling back to the hero subtitle."""
        return self.short_summary or self.hero_subtitle

    def related_services(self):
        """Sibling services in the same category, for the 'Related modalities' section."""
        if not self.category:
            return Service.objects.none()
        return Service.objects.filter(
            category=self.category, is_published=True
        ).exclude(pk=self.pk).order_by('id')

    def whatsapp_cta_text(self):
        return self.cta_whatsapp_message or "Hello, I'm interested in {}".format(self.title)

    def get_first_header(self):
        part1 = str(self.content).split('<h')[1]
        part2 = part1.split('</h')[0]
        part3 = part2.split('>')[1]
        return part3

    def get_first_para_preview(self):
        first_para = str(self.content).split('</p>')[0].split('<p>')[1]
        first_twenty = first_para.split(' ')[:6]
        if first_twenty[-1][-1] == ',':
            first_twenty[-1] = first_twenty[-1][:-1]
        excerpt = '{}...'.format(' '.join(first_twenty), '...')
        return excerpt

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.get_paragraph_preview(str(self.content))
        return super(Service, self).save(*args, **kwargs)

    def get_paragraph_preview(self, content):
        preview = ''
        try:
            first_para = str(content).split('</p>')[0].split('<p>')[1]
            first_twenty = first_para.split(' ')[:35]
            if first_twenty[-1][-1] == ',':
                first_twenty[-1] = first_twenty[-1][:-1]
            preview = '{}...'.format(' '.join(first_twenty), '...')
        except IndexError as ie:
            print(str(ie))
            preview = content
        return preview


class ServiceFAQ(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = RichTextUploadingField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{} — {}'.format(self.service.title, self.question)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Service FAQ'
        verbose_name_plural = 'Service FAQs'


class ServicesHubPage(models.Model):
    VIDEO_SOURCE_NONE = 'none'
    VIDEO_SOURCE_FILE = 'file'
    VIDEO_SOURCE_YOUTUBE = 'youtube'
    VIDEO_SOURCE_CHOICES = [
        (VIDEO_SOURCE_NONE, 'No video (hide section)'),
        (VIDEO_SOURCE_FILE, 'Self-hosted file'),
        (VIDEO_SOURCE_YOUTUBE, 'YouTube embed'),
    ]

    hub_heading = models.CharField(
        max_length=200, blank=True, default='',
        help_text="Defaults to 'Counselling & Therapy Services' if left blank."
    )
    hub_intro = models.TextField(
        blank=True, default='',
        help_text="50-80 word introductory paragraph under the hero heading."
    )

    # "Why Choose Another Light Counselling?" section
    why_choose_intro = models.CharField(
        max_length=300, blank=True, default='',
        help_text="Single line under the 'Why Choose Another Light Counselling?' heading."
    )
    why_choose_points = models.TextField(
        blank=True, default='',
        help_text="One point per line, e.g. 'Experienced therapists'. Leave blank to hide the whole section."
    )

    # "Our Therapy Process" — simple 4-step visual
    process_step1_title = models.CharField(max_length=100, blank=True, default='')
    process_step1_detail = models.CharField(max_length=250, blank=True, default='')
    process_step2_title = models.CharField(max_length=100, blank=True, default='')
    process_step2_detail = models.CharField(max_length=250, blank=True, default='')
    process_step3_title = models.CharField(max_length=100, blank=True, default='')
    process_step3_detail = models.CharField(max_length=250, blank=True, default='')
    process_step4_title = models.CharField(max_length=100, blank=True, default='')
    process_step4_detail = models.CharField(max_length=250, blank=True, default='')

    video_source = models.CharField(
        max_length=10, choices=VIDEO_SOURCE_CHOICES, default=VIDEO_SOURCE_NONE,
        help_text="Switch between a self-hosted video file and a YouTube embed, or hide the video slot entirely."
    )
    video_file = models.FileField(upload_to='services_hub', blank=True, null=True)
    video_youtube_url = models.URLField(
        blank=True, default='',
        help_text="Full YouTube watch/share URL. Only used when Video source is 'YouTube embed'."
    )
    video_poster = models.ImageField(
        upload_to='services_hub', blank=True,
        help_text="Optional poster/thumbnail image shown before a self-hosted video plays."
    )
    video_caption = models.CharField(max_length=300, blank=True, default='')

    def has_video(self):
        if self.video_source == self.VIDEO_SOURCE_FILE:
            return bool(self.video_file)
        if self.video_source == self.VIDEO_SOURCE_YOUTUBE:
            return bool(self.video_youtube_url)
        return False

    def why_choose_list(self):
        return [line.strip() for line in self.why_choose_points.splitlines() if line.strip()]

    def process_steps(self):
        steps = []
        for n in (1, 2, 3, 4):
            title = getattr(self, 'process_step{}_title'.format(n))
            if title:
                steps.append({'order': n, 'title': title, 'detail': getattr(self, 'process_step{}_detail'.format(n))})
        return steps

    def youtube_embed_url(self):
        if self.video_source != self.VIDEO_SOURCE_YOUTUBE or not self.video_youtube_url:
            return ''
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.video_youtube_url)
        video_id = ''
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/')
        elif 'youtube.com' in parsed.netloc:
            video_id = parse_qs(parsed.query).get('v', [''])[0]
        return 'https://www.youtube.com/embed/{}'.format(video_id) if video_id else ''

    def __str__(self):
        return 'Services Hub Page'

    class Meta:
        verbose_name = 'Services Hub Page'
        verbose_name_plural = 'Services Hub Page'


class DoIFeel(models.Model):
    image_file = models.ImageField(upload_to='doifeels', blank=True)
    title = models.CharField(max_length=250)
    content = RichTextUploadingField()
    slug = models.SlugField(max_length=100, blank=True)

    # SEO FIELDS
    meta_title = models.CharField(max_length=250, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return str(self.title)

    def get_first_header(self):
        part1 = str(self.content).split('<h')[1]
        part2 = part1.split('</h')[0]
        part3 = part2.split('>')[1]
        return part3

    def get_first_para_preview(self):
        first_para = str(self.content).split('</p>')[0].split('<p>')[1]
        first_twenty = first_para.split(' ')[:6]
        if first_twenty[-1][-1] == ',':
            first_twenty[-1] = first_twenty[-1][:-1]
        excerpt = '{}...'.format(' '.join(first_twenty), '...')
        return excerpt

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.get_paragraph_preview(str(self.content))
        return super(DoIFeel, self).save(*args, **kwargs)

    def get_paragraph_preview(self, content):
        preview = ''
        try:
            first_para = str(content).split('</p>')[0].split('<p>')[1]
            first_twenty = first_para.split(' ')[:35]
            if first_twenty[-1][-1] == ',':
                first_twenty[-1] = first_twenty[-1][:-1]
            preview = '{}...'.format(' '.join(first_twenty), '...')
        except IndexError as ie:
            print(str(ie))
            preview = content
        return preview


class Jd(models.Model):
    image_file = models.ImageField(upload_to='careers', blank=True)
    title = models.CharField(max_length=250, blank=True)
    content = RichTextUploadingField(blank=True)
    slug = models.SlugField(max_length=100, blank=True)

    # SEO FIELDS
    meta_title = models.CharField(max_length=250, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.CharField(max_length=500, blank=True, default='')

    # Add your new link fields here
    apply_link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.title)

    def get_first_header(self):
        part1 = str(self.content).split('<h')[1]
        part2 = part1.split('</h')[0]
        part3 = part2.split('>')[1]
        return part3

    def get_first_para_preview(self):
        first_para = str(self.content).split('</p>')[0].split('<p>')[1]
        first_twenty = first_para.split(' ')[:6]
        if first_twenty[-1][-1] == ',':
            first_twenty[-1] = first_twenty[-1][:-1]
        excerpt = '{}...'.format(' '.join(first_twenty), '...')
        return excerpt

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.get_paragraph_preview(str(self.content))
        return super(Jd, self).save(*args, **kwargs)

    def get_paragraph_preview(self, content):
        preview = ''
        try:
            first_para = str(content).split('</p>')[0].split('<p>')[1]
            first_twenty = first_para.split(' ')[:35]
            if first_twenty[-1][-1] == ',':
                first_twenty[-1] = first_twenty[-1][:-1]
            preview = '{}...'.format(' '.join(first_twenty), '...')
        except IndexError as ie:
            print(str(ie))
            preview = content
        return preview

    class Meta:
        verbose_name = 'Jd'
        verbose_name_plural = 'Careers'


class Post(models.Model):
    image_file = models.ImageField(upload_to='post_headers')
    title = models.CharField(max_length=250)
    # p_type=models.ForeignKey(PostType, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    # SEO FIELDS
    meta_title = models.CharField(max_length=250, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.CharField(max_length=500, blank=True, default='')

    def save(self, *args, **kwargs):
        # UPDATE TIMESTAMPS
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()

        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.title)

        # SET META TITLE AND DESCRIPTIONS IF NOT MANUALLY SET
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.get_paragraph_preview(str(self.content))

        # FINALLY, RETURN super
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('post', args=[str(self.slug)])

    def get_paragraph_preview(self, content):
        preview = ''
        try:
            first_para = str(content).split('</p>')[0].split('<p>')[1]
            first_twenty = first_para.split(' ')[:35]
            if first_twenty[-1][-1] == ',':
                first_twenty[-1] = first_twenty[-1][:-1]
            preview = '{}...'.format(' '.join(first_twenty), '...')
        except IndexError as ie:
            print(str(ie))
            preview = content
        return preview

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class Policy(models.Model):
    title = models.CharField(max_length=250)
    content = RichTextUploadingField(max_length=40000)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs):
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.title)
        # FINALLY, RETURN super
        return super(Policy, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'


class Committee(models.Model):
    title = models.CharField(max_length=250)
    content = RichTextUploadingField(max_length=40000)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs):
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.title)
        # FINALLY, RETURN super
        return super(Committee, self).save(*args, **kwargs)


class DynamicContent(models.Model):
    key = models.CharField(max_length=250)
    title = models.CharField(max_length=250, blank=True)
    content = RichTextUploadingField(max_length=40000, blank=True)
    image_file = models.ImageField(upload_to='dynamic_images', blank=True)

    class Meta:
        verbose_name = 'Dynamic Content'
        verbose_name_plural = 'Dynamic Content'


# --------- NEW: Team Page singleton for hero/intro copy ---------
class TeamPage(models.Model):
    hero_title = models.CharField(max_length=120)
    hero_subtitle = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to='team', blank=True)
    intro_richtext = RichTextUploadingField(blank=True)
    seo_title = models.CharField(max_length=250, blank=True, default='')
    seo_description = models.TextField(blank=True, default='')

    def __str__(self):
        return "Team Page"


class OnboardingPlan(models.Model):
    # — PAGE META
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    subheading = models.TextField(blank=True)

    cta_primary = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. 'Pick a Plan'"
    )
    cta_primary_url = models.URLField(blank=True)
    cta_secondary = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. 'Speak to Us'"
    )
    cta_secondary_url = models.URLField(blank=True)

    # — ONBOARDING STEPS (1–3)
    step1_title = models.CharField(max_length=100, blank=True)
    step1_detail = models.TextField(blank=True)
    step1_icon = models.ImageField(upload_to="onboarding/icons", blank=True)

    step2_title = models.CharField(max_length=100, blank=True)
    step2_detail = models.TextField(blank=True)
    step2_icon = models.ImageField(upload_to="onboarding/icons", blank=True)

    step3_title = models.CharField(max_length=100, blank=True)
    step3_detail = models.TextField(blank=True)
    step3_icon = models.ImageField(upload_to="onboarding/icons", blank=True)

    # — PLAN OPTION 1
    plan1_name = models.CharField(max_length=100, blank=True)
    plan1_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan1_features = models.TextField(help_text="One feature per line", blank=True)
    plan1_prerequisites = models.CharField(max_length=200, blank=True)
    plan1_combo_tag = models.CharField(max_length=50, blank=True)
    plan1_is_combo = models.BooleanField(default=False)
    plan1_order = models.PositiveSmallIntegerField(default=1)

    # — PLAN OPTION 2
    plan2_name = models.CharField(max_length=100, blank=True)
    plan2_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan2_features = models.TextField(help_text="One feature per line", blank=True)
    plan2_prerequisites = models.CharField(max_length=200, blank=True)
    plan2_combo_tag = models.CharField(max_length=50, blank=True)
    plan2_is_combo = models.BooleanField(default=False)
    plan2_order = models.PositiveSmallIntegerField(default=2)

    # — PLAN OPTION 3
    plan3_name = models.CharField(max_length=100, blank=True)
    plan3_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan3_features = models.TextField(help_text="One feature per line", blank=True)
    plan3_prerequisites = models.CharField(max_length=200, blank=True)
    plan3_combo_tag = models.CharField(max_length=50, blank=True)
    plan3_is_combo = models.BooleanField(default=False)
    plan3_order = models.PositiveSmallIntegerField(default=3)

    # — PLAN OPTION 4
    plan4_name = models.CharField(max_length=100, blank=True)
    plan4_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan4_features = models.TextField(help_text="One feature per line", blank=True)
    plan4_prerequisites = models.CharField(max_length=200, blank=True)
    plan4_combo_tag = models.CharField(max_length=50, blank=True)
    plan4_is_combo = models.BooleanField(default=False)
    plan4_order = models.PositiveSmallIntegerField(default=4)

    # — COMBO OPTION A (05A)
    plan5_name = models.CharField(max_length=100, blank=True)
    plan5_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan5_features = models.TextField(help_text="One feature per line", blank=True)
    plan5_prerequisites = models.CharField(max_length=200, blank=True)
    plan5_combo_tag = models.CharField(max_length=50, blank=True)
    plan5_is_combo = models.BooleanField(default=True)
    plan5_order = models.PositiveSmallIntegerField(default=5)

    # — COMBO OPTION B (05B)
    plan6_name = models.CharField(max_length=100, blank=True)
    plan6_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan6_features = models.TextField(help_text="One feature per line", blank=True)
    plan6_prerequisites = models.CharField(max_length=200, blank=True)
    plan6_combo_tag = models.CharField(max_length=50, blank=True)
    plan6_is_combo = models.BooleanField(default=True)
    plan6_order = models.PositiveSmallIntegerField(default=6)

    # — COMBO OPTION C (05C)
    plan7_name = models.CharField(max_length=100, blank=True)
    plan7_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan7_features = models.TextField(help_text="One feature per line", blank=True)
    plan7_prerequisites = models.CharField(max_length=200, blank=True)
    plan7_combo_tag = models.CharField(max_length=50, blank=True)
    plan7_is_combo = models.BooleanField(default=True)
    plan7_order = models.PositiveSmallIntegerField(default=7)

    # — SUPERSAVER COMBO D (05D)
    plan8_name = models.CharField(max_length=100, blank=True)
    plan8_price = models.PositiveIntegerField(help_text="In rupees", blank=True, null=True)
    plan8_features = models.TextField(help_text="One feature per line", blank=True)
    plan8_prerequisites = models.CharField(max_length=200, blank=True)
    plan8_combo_tag = models.CharField(max_length=50, blank=True)
    plan8_is_combo = models.BooleanField(default=True)
    plan8_order = models.PositiveSmallIntegerField(default=8)

    # — RENEWAL OPTIONS
    renewal1_name = models.CharField(max_length=100, blank=True)
    renewal1_price = models.PositiveIntegerField(blank=True, null=True)
    renewal1_description = models.TextField(blank=True)
    renewal1_order = models.PositiveSmallIntegerField(default=1)

    renewal2_name = models.CharField(max_length=100, blank=True)
    renewal2_price = models.PositiveIntegerField(blank=True, null=True)
    renewal2_description = models.TextField(blank=True)
    renewal2_order = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return f"Workshop: {self.tagline}"

class MediaFeature(models.Model):
    FEATURE_TYPE_CHOICES = [
        ('logo',    'Press logo — carousel / homepage strip'),
        ('video',   'Video highlight — YouTube'),
        ('article', 'Article card — with READ button'),
        ('more',    'More features — simple text link'),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)

    feature_type = models.CharField(
        max_length=10,
        choices=FEATURE_TYPE_CHOICES,
        default='logo',
        help_text="Which block this appears in on the Media Features page. "
                  "'logo' also powers the homepage press strip."
    )
    outlet_name = models.CharField(
        max_length=200,
        help_text="Publication name, e.g. 'Vogue India', 'The Hindu'."
    )
    logo = models.ImageField(
        upload_to='media_features',
        blank=True,
        help_text="Transparent PNG works best. Used for logo carousel and article cards. "
                  "Not needed for video or 'more' links."
    )
    logo_alt = models.CharField(
        max_length=200, blank=True, default='',
        help_text="Alt text for the logo. Leave blank to fall back to the outlet name."
    )
    kicker = models.CharField(
        max_length=120, blank=True, default='',
        help_text="Small label shown above an article card's title, "
                  "e.g. 'Vogue Warriors', 'Tips for parents'."
    )
    article_title = models.CharField(
        max_length=300, blank=True, default='',
        help_text="For logos: caption on hover. For video/article/more: the headline shown."
    )
    description = models.TextField(
        blank=True, default='',
        help_text="Short excerpt shown on article cards (the READ cards)."
    )
    video_url = models.URLField(
        max_length=1000, blank=True, default='',
        help_text="For 'video' type only. Paste a normal YouTube link "
                  "(watch, youtu.be, shorts or embed) — the site converts it automatically."
    )
    link = models.URLField(
        max_length=1000, blank=True, default='',
        help_text="Full URL the logo / READ button / more-feature line points to."
    )
    order = models.PositiveIntegerField(
        default=1,
        help_text="Lower numbers appear first, within each block."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Untick to hide without deleting."
    )

    def __str__(self):
        return f"{self.get_feature_type_display()} — {self.outlet_name}"

    @property
    def youtube_id(self):
        """Pull the 11-char video id out of any common YouTube URL form."""
        import re
        url = (self.video_url or "").strip()
        if not url:
            return ""
        patterns = [
            r"youtube\.com/watch\?(?:.*&)?v=([A-Za-z0-9_-]{11})",
            r"youtu\.be/([A-Za-z0-9_-]{11})",
            r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
            r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
        ]
        for p in patterns:
            m = re.search(p, url)
            if m:
                return m.group(1)
        return ""

    @property
    def youtube_embed_url(self):
        vid = self.youtube_id
        return f"https://www.youtube.com/embed/{vid}" if vid else ""

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Media Feature'
        verbose_name_plural = 'Media Features'