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

    def __str__(self):
        return str(self.question)

class Resource(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=500)
    thumbnail = models.ImageField(upload_to='photographs')
    link = models.CharField(max_length=1000)



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

 
class Post(models.Model):
    # image_file = models.ImageField(upload_to='photographs')
    title = models.CharField(max_length=250)
    p_type=models.ForeignKey(PostType, on_delete=models.CASCADE)
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