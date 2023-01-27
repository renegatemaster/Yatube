from django.test import TestCase, Client
from http import HTTPStatus


class ViewTestClass(TestCase):

    def setUp(self):
        self.client = Client()

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        # Проверьте, что статус ответа сервера - 404
        # Проверьте, что используется шаблон core/404.html
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
