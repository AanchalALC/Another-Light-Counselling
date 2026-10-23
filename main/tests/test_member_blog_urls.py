from django.test import SimpleTestCase
from django.urls import reverse


class MemberBlogCanonicalURLTests(SimpleTestCase):
    def test_reversed_member_blog_urls_have_no_trailing_slash(self):
        self.assertEqual(
            reverse('member-blog-list', args=['therapist']),
            '/about/therapist/blogs',
        )
        self.assertEqual(
            reverse('member-blog-detail', args=['therapist', 'post']),
            '/about/therapist/blogs/post',
        )

    def test_member_blog_list_trailing_slash_redirects_to_canonical_url(self):
        response = self.client.get('/about/therapist/blogs/?page=2')

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/about/therapist/blogs?page=2')

    def test_member_blog_detail_trailing_slash_redirects_to_canonical_url(self):
        response = self.client.get('/about/therapist/blogs/post/?source=email')

        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response['Location'],
            '/about/therapist/blogs/post?source=email',
        )
