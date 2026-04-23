from django.test import SimpleTestCase


class ShopViewsTest(SimpleTestCase):
    def test_main_page_status(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_subpage_status(self):
        response = self.client.get('/page/1/')
        self.assertEqual(response.status_code, 200)
