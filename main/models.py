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
    # AVAIL_CHOICES = (
    #     ('open',        'Accepting new clients'),
    #     ('waitlist',    'Waitlist only'),
    #     ('unavailable', 'Not taking clients'),
    # )
    # availability = models.CharField(max_length=12, choices=AVAIL_CHOICES, default='open')

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
        base = (slugify(base) or 'member')[:110]
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
    image_file = models.ImageField(upload_to='services', blank=True)
    title = models.CharField(max_length=250)
    img_alt_text = models.CharField(max_length=250, blank=True, default='')
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
    slug = models.SlugField(max_length=200, unique=True)
    tagline = models.CharField(max_length=200)
    subheading = models.TextField()

    cta_primary = models.CharField(
        max_length=50,
        help_text="e.g. 'Pick a Plan'"
    )
    cta_primary_url = models.URLField(blank=True)
    cta_secondary = models.CharField(
        max_length=50,
        help_text="e.g. 'Speak to Us'"
    )
    cta_secondary_url = models.URLField(blank=True)

    # — ONBOARDING STEPS (1–3)
    step1_title = models.CharField(max_length=100)
    step1_detail = models.TextField()
    step1_icon = models.ImageField(upload_to="onboarding/icons", blank=True)

    step2_title = models.CharField(max_length=100)
    step2_detail = models.TextField()
    step2_icon = models.ImageField(upload_to="onboarding/icons", blank=True)

    step3_title = models.CharField(max_length=100)
    step3_detail = models.TextField()
    step3_icon = models.ImageField(upload_to="onboarding/icons", blank=True)

    # — PLAN OPTION 1
    plan1_name = models.CharField(max_length=100)
    plan1_price = models.PositiveIntegerField(help_text="In rupees")
    plan1_features = models.TextField(help_text="One feature per line")
    plan1_prerequisites = models.CharField(max_length=200, blank=True)
    plan1_combo_tag = models.CharField(max_length=50, blank=True)
    plan1_is_combo = models.BooleanField(default=False)
    plan1_order = models.PositiveSmallIntegerField(default=1)

    # — PLAN OPTION 2
    plan2_name = models.CharField(max_length=100)
    plan2_price = models.PositiveIntegerField(help_text="In rupees")
    plan2_features = models.TextField(help_text="One feature per line")
    plan2_prerequisites = models.CharField(max_length=200, blank=True)
    plan2_combo_tag = models.CharField(max_length=50, blank=True)
    plan2_is_combo = models.BooleanField(default=False)
    plan2_order = models.PositiveSmallIntegerField(default=2)

    # — PLAN OPTION 3
    plan3_name = models.CharField(max_length=100)
    plan3_price = models.PositiveIntegerField(help_text="In rupees")
    plan3_features = models.TextField(help_text="One feature per line")
    plan3_prerequisites = models.CharField(max_length=200, blank=True)
    plan3_combo_tag = models.CharField(max_length=50, blank=True)
    plan3_is_combo = models.BooleanField(default=False)
    plan3_order = models.PositiveSmallIntegerField(default=3)

    # — PLAN OPTION 4
    plan4_name = models.CharField(max_length=100)
    plan4_price = models.PositiveIntegerField(help_text="In rupees")
    plan4_features = models.TextField(help_text="One feature per line")
    plan4_prerequisites = models.CharField(max_length=200, blank=True)
    plan4_combo_tag = models.CharField(max_length=50, blank=True)
    plan4_is_combo = models.BooleanField(default=False)
    plan4_order = models.PositiveSmallIntegerField(default=4)

    # — COMBO OPTION A (05A)
    plan5_name = models.CharField(max_length=100)
    plan5_price = models.PositiveIntegerField(help_text="In rupees")
    plan5_features = models.TextField(help_text="One feature per line")
    plan5_prerequisites = models.CharField(max_length=200, blank=True)
    plan5_combo_tag = models.CharField(max_length=50, blank=True)
    plan5_is_combo = models.BooleanField(default=True)
    plan5_order = models.PositiveSmallIntegerField(default=5)

    # — COMBO OPTION B (05B)
    plan6_name = models.CharField(max_length=100)
    plan6_price = models.PositiveIntegerField(help_text="In rupees")
    plan6_features = models.TextField(help_text="One feature per line")
    plan6_prerequisites = models.CharField(max_length=200, blank=True)
    plan6_combo_tag = models.CharField(max_length=50, blank=True)
    plan6_is_combo = models.BooleanField(default=True)
    plan6_order = models.PositiveSmallIntegerField(default=6)

    # — COMBO OPTION C (05C)
    plan7_name = models.CharField(max_length=100)
    plan7_price = models.PositiveIntegerField(help_text="In rupees")
    plan7_features = models.TextField(help_text="One feature per line")
    plan7_prerequisites = models.CharField(max_length=200, blank=True)
    plan7_combo_tag = models.CharField(max_length=50, blank=True)
    plan7_is_combo = models.BooleanField(default=True)
    plan7_order = models.PositiveSmallIntegerField(default=7)

    # — SUPERSAVER COMBO D (05D)
    plan8_name = models.CharField(max_length=100)
    plan8_price = models.PositiveIntegerField(help_text="In rupees")
    plan8_features = models.TextField(help_text="One feature per line")
    plan8_prerequisites = models.CharField(max_length=200, blank=True)
    plan8_combo_tag = models.CharField(max_length=50, blank=True)
    plan8_is_combo = models.BooleanField(default=True)
    plan8_order = models.PositiveSmallIntegerField(default=8)

    # — RENEWAL OPTIONS
    renewal1_name = models.CharField(max_length=100)
    renewal1_price = models.PositiveIntegerField()
    renewal1_description = models.TextField()
    renewal1_order = models.PositiveSmallIntegerField(default=1)

    renewal2_name = models.CharField(max_length=100)
    renewal2_price = models.PositiveIntegerField()
    renewal2_description = models.TextField()
    renewal2_order = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return f"Workshop: {self.tagline}"
