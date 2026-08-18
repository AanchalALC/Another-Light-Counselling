from django.test import Client, TestCase, override_settings


class CanonicalHostRedirectMiddlewareTestCase(TestCase):

    @override_settings(CANONICAL_REDIRECT_ENABLED=True)
    def test_apex_host_redirects_to_www_and_keeps_query_string(self):
        client = Client()
        response = client.get(
            '/service/trauma-therapy?utm_source=x', HTTP_HOST='another-light.com'
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response['Location'],
            'https://www.another-light.com/service/trauma-therapy?utm_source=x',
        )

    @override_settings(CANONICAL_REDIRECT_ENABLED=True)
    def test_www_host_is_not_redirected_by_this_middleware(self):
        client = Client()
        response = client.get('/this-path-does-not-exist/', HTTP_HOST='www.another-light.com')
        self.assertEqual(response.status_code, 404)

    @override_settings(CANONICAL_REDIRECT_ENABLED=True)
    def test_health_check_host_is_not_redirected(self):
        client = Client()
        response = client.get('/this-path-does-not-exist/', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 404)

    @override_settings(CANONICAL_REDIRECT_ENABLED=True)
    def test_apex_host_with_port_is_redirected_and_port_is_stripped(self):
        client = Client()
        response = client.get('/service/trauma-therapy', HTTP_HOST='another-light.com:443')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response['Location'],
            'https://www.another-light.com/service/trauma-therapy',
        )

    @override_settings(CANONICAL_REDIRECT_ENABLED=False)
    def test_no_redirect_when_disabled(self):
        client = Client()
        response = client.get('/this-path-does-not-exist/', HTTP_HOST='another-light.com')
        self.assertEqual(response.status_code, 404)
