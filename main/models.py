from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.sites.models import Site
 
class PostType(models.Model):
    type_name = models.CharField(max_length=30)
 
    def __str__(self):
        return str(self.type_name)


class FAQ(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    question = models.CharField(max_length=500)
    answer = RichTextUploadingField(max_length=14000)
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

    

class Member(models.Model):
    thumbnail = models.ImageField(upload_to='members')
    name = models.CharField(max_length=700)
    designation = models.CharField(max_length=700)
    info = RichTextUploadingField(max_length=14000)
    # readmore = models.CharField(max_length=900, default='')
    
    # HELPER VARIABLE
    layout_position = ''

    def generate_tooltip_markup(self):
        self.tippy_info = self.info
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
            self.tippy_info = str(self.tippy_info).replace(
                word, 
                '<span class="mytooltip {word}tippy">{word}</span>'.format(word=word)
            )

    def __str__(self):
        return str(self.name)



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
    title = models.CharField(max_length=250)
    content = RichTextUploadingField(max_length=14000)
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
        # remove comma from last
        if first_twenty[-1][-1] == ',':
            first_twenty[-1] = first_twenty[-1][:-1]

        excerpt = '{}...'.format(' '.join(first_twenty), '...')

        return excerpt

    def save(self, *args, **kwargs):

        # GENERATE TITLE
        # try:
        #     self.title = self.get_first_header()
        # except IndexError:
        #     self.title = self.get_first_para_preview()


        # GENERATE SLUG
        if not self.slug or self.slug == '':
            self.slug = slugify(self.title)

        
        # SET META TITLE AND DESCRIPTIONS IF NOT MANUALLY SET
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
            # remove comma from last
            if first_twenty[-1][-1] == ',':
                first_twenty[-1] = first_twenty[-1][:-1]

            preview = '{}...'.format(' '.join(first_twenty), '...')
        except IndexError as ie:
            print(str(ie))
            preview = content

        return preview



        
 
class Post(models.Model):
    image_file = models.ImageField(upload_to='post_headers')
    title = models.CharField(max_length=250)
    # p_type=models.ForeignKey(PostType, on_delete=models.CASCADE)
    content = RichTextUploadingField(max_length=14000)
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
            # remove comma from last
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

    

