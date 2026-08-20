from django.conf import settings
from django.contrib.sitemaps import Sitemap
from .models import Post, PostType, DoIFeel, Service
from django.urls import reverse


class _CanonicalSite:
    def __init__(self, domain):
        self.domain = domain


class CanonicalDomainSitemap(Sitemap):
    # Migrations are gitignored in this repo, so the sites.Site row for
    # SITE_ID can't be pinned in version control — hardcode the domain
    # instead of relying on django.contrib.sites.
    protocol = 'https'

    def get_urls(self, page=1, site=None, protocol=None):
        site = _CanonicalSite(getattr(settings, 'CANONICAL_HOST', 'www.another-light.com'))
        return super().get_urls(page=page, site=site, protocol=protocol)


class StaticSiteMap(CanonicalDomainSitemap):
    changefreq = "monthly"

    def items(self):
        return [
            'index',
            'about',
            'services',
            'faqs',
            'resources',
            'reviews',
            'contact',
            # 'doifeel' removed: its URL pattern requires a <slug:slug> arg,
            # so reverse('doifeel') with no args raised NoReverseMatch.
            # See DoIFeelSiteMap below for the per-object entries.
            'careers',
            'blog',
            'media-features',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'index':
            return 1.0
        else:
            return 0.9

class PostSiteMap(CanonicalDomainSitemap):
    changefreq = "monthly"
    priority = 0.64

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.modified


class PostTypeSiteMap(CanonicalDomainSitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return PostType.objects.all()


class DoIFeelSiteMap(CanonicalDomainSitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return DoIFeel.objects.all()

    def location(self, obj):
        return reverse('doifeel', args=[obj.slug])


class ServiceSiteMap(CanonicalDomainSitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        # Unpublished rows (e.g. ISP/Brainspotting pending SEO sign-off) stay out
        # until is_published is switched on.
        return Service.objects.filter(is_published=True)

    def location(self, obj):
        return reverse('service', args=[obj.slug])
