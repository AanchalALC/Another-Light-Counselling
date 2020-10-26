from django.test import TestCase

class ViewsTestCase(TestCase):

    def has_missing_links(self, response):
        # GET STRING
        raw_content = str(response.content)

        # REMOVE HTML WHERE '#' LINK IS INTENTIONAL
        content = raw_content.replace('<a href="#" id="closemenu">', '')
        content = content.replace('<a href="#">OK</a>', '')

        # CHECK PRESENCE OF UNHANDLED LINK
        has_empty_links = 'href="#"' in content

        # IF THERE IS AN EMPTY LINK, FIND THE LINE AND PRINT IT
        if has_empty_links:
            lines = content.split('\\n')
            # print(lines[1])

            for i in range(0, len(lines)):
                line = lines[i]
                if 'href="#"' in line:
                    msg = '{}: {}'.format(i, line)
                    print(msg)
        
        # RETURN
        return has_empty_links


    def test_home(self):
        print('Test home')
        resp = self.client.get('')
        
        # CHECK IF RECIEVED RESPONSE
        self.assertEqual(resp.status_code, 200)

        # CHECK THAT THERE ARE NO EMPTY LINKS
        self.assertFalse(self.has_missing_links(resp))

    def test_about(self):
        print('Test about')
        resp = self.client.get('/about')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.has_missing_links(resp))

    def test_faqs(self):
        print('Test FAQS')
        resp = self.client.get('/faqs')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.has_missing_links(resp))

    def test_resources(self):
        print('Test Resource')
        page = '/resources'
        
        resp = self.client.get(page)
        self.assertEqual(resp.status_code, 200, msg=f"{page} not found...")
        self.assertFalse(self.has_missing_links(resp))

    def test_reviews(self):
        print('Test Reviews')
        page = '/reviews'
        
        resp = self.client.get(page)
        self.assertEqual(resp.status_code, 200, msg=f"{page} not found...")
        self.assertFalse(self.has_missing_links(resp))

    def test_contact(self):
        print('Test Contact')
        page = '/contact'
        
        resp = self.client.get(page)
        self.assertEqual(resp.status_code, 200, msg=f"{page} not found...")
        self.assertFalse(self.has_missing_links(resp))