from django.contrib.sitemaps import Sitemap
from .models import Post, PostType
from django.urls import reverse


class StaticSiteMap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'

    def items(self):
        return [
            'index',
            'about',
            'faqs',
            'resources',
            'reviews',
            'contact',
            'doifeel',
            # 'howtofeel',
            'blog'
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'index':
            return 1.0
        else:
            return 0.9

class PostSiteMap(Sitemap):
    changefreq = "monthly"
    priority = 0.64
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