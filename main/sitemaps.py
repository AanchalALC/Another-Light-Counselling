from django.contrib.sitemaps import Sitemap
from .models import Post, PostType

class PostSiteMap(Sitemap):
    changefreq = "monthly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.modified


class PostTypeSiteMap(Sitemap):
    changefreq = "monthly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return PostType.objects.all()