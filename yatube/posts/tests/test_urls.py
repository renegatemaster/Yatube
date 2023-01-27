from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from posts.models import Post, Group
from http import HTTPStatus


User = get_user_model()


class TestURL(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='DudYura')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.user1 = User.objects.create(username='NoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user1)
        cls.group = Group.objects.create(
            title='Журналюги',
            slug='journalists',
            description='В поисках истины'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def test_guest_pages_status(self):
        addresses_code = {
            '/': HTTPStatus.OK,
            '/group/journalists/': HTTPStatus.OK,
            '/profile/DudYura/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in addresses_code.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_post_edit_author(self):
        response = self.author_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_authorized(self):
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_post_edit_guest(self):
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_create_post_authorized(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_guest(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_add_comment_guest(self):
        response = self.guest_client.get('/posts/1/comment/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')

    def test_follow_guest(self):
        response = self.guest_client.get('/follow/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/follow/')

    def test_follow_authorized(self):
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template(self):
        cache.clear()
        templates_addresses = {
            '/': 'posts/index.html',
            '/group/journalists/': 'posts/group_list.html',
            '/profile/DudYura/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/update_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_addresses.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
