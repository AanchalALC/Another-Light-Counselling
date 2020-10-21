from django.test import TestCase

class ViewsTestCase(TestCase):
    def test_home(self):
        print('Test home')
        resp = self.client.get('')
        self.assertEqual(resp.status_code, 200)

    def test_about(self):
        print('Test about')
        resp = self.client.get('/about')
        self.assertEqual(resp.status_code, 200)

    def test_faqs(self):
        print('Test FAQS')
        resp = self.client.get('/faqs')
        self.assertEqual(resp.status_code, 200)

    def test_resources(self):
        print('Test Resource')
        page = '/resources'
        
        resp = self.client.get(page)
        self.assertEqual(resp.status_code, 200, msg=f"{page} not found...")