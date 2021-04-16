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

    def __str__(self):
        name = str(self.title)
        val = str(self.value)

        return f'{name}: {val}'

    class Meta:
        verbose_name = 'Another Light Contact Detail'
        verbose_name_plural = 'Another Light Contact Details'
 
class Post(models.Model):
    image_file = models.ImageField(upload_to='post_headers')
    title = models.CharField(max_length=250)
    # p_type=models.ForeignKey(PostType, on_delete=models.CASCADE)
    content = RichTextUploadingField(max_length=14000)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
 
    def save(self, *args, **kwargs):
        # UPDATE TIMESTAMPS
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)
 
    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('post', args=[str(self.slug)])
 
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'