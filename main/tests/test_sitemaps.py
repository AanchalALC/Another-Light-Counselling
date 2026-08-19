import re

from django.test import TestCase


class SitemapTestCase(TestCase):

    def test_sitemap_urls_use_canonical_www_domain(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

        body = response.content.decode('utf-8')
        locs = re.findall(r'<loc>(.*?)</loc>', body)

        self.assertTrue(locs)
        for loc in locs:
            self.assertTrue(
                loc.startswith('https://www.another-light.com/'),
                msg='{} does not start with https://www.another-light.com/'.format(loc),
            )

        self.assertEqual(body.count('example.com'), 0)

        # The sitemaps.org XML namespace itself is a fixed http:// URI (not a
        # page URL) and is required for the document to be a valid sitemap,
        # so exclude it before checking that no URL leaked an http:// scheme.
        body_without_namespace = body.replace(
            'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', ''
        )
        self.assertEqual(body_without_namespace.count('http://'), 0)
