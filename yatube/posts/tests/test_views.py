import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from posts.models import Post, Group, Comment, Follow
from django import forms
from django.urls import reverse


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='DudYura')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Журналюги',
            slug='journalists',
            description='В поисках истины'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.bulk_posts: list = []
        for i in range(13):
            cls.bulk_posts.append(Post(text=f'Тестовый текст {i}',
                                       author=cls.user,
                                       group=cls.group,
                                       image=cls.uploaded
                                       ))
        Post.objects.bulk_create(cls.bulk_posts)
        cls.comment = Comment.objects.create(
            post=Post.objects.get(pk=1),
            author=cls.user,
            text='Проверяем комменты',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={
                'slug': 'journalists'}),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': 'DudYura'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={
                'post_id': 1}),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/update_post.html': reverse('posts:post_edit', kwargs={
                'post_id': 1})
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """В контекст страницы index передаются ожидаемые объекты."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, 'Тестовый текст 12')
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)
        self.assertTrue(first_object.image)

    def test_paginator(self):
        """Паджинатор передаёт необходимое количество объектов."""
        cache.clear()
        addresses_objects = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 3,
            reverse('posts:group_list', kwargs={'slug': 'journalists'}): 10,
            reverse('posts:group_list',
                    kwargs={'slug': 'journalists'}) + '?page=2': 3,
            reverse('posts:profile', kwargs={'username': 'DudYura'}): 10,
            reverse('posts:profile',
                    kwargs={'username': 'DudYura'}) + '?page=2': 3,
        }
        for address, object in addresses_objects.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(len(response.context['page_obj']), object)

    def test_group_list_context(self):
        """В контекст страницы group_list передаются ожидаемые объекты."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'journalists'}))
        objects = response.context['page_obj']
        for obj in objects:
            self.assertEqual(obj.group, self.group)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, 'Тестовый текст 12')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertTrue(post.image)

    def test_profile_context(self):
        """В контекст страницы profile передаются ожидаемые объекты."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'DudYura'}))
        objects = response.context['page_obj']
        for obj in objects:
            self.assertEqual(obj.author, self.user)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, 'Тестовый текст 12')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertTrue(post.image)

    def test_post_detail_context(self):
        """В контекст страницы post_detail передаются ожидаемые объекты."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        self.assertEqual(response.context['post'].id, 1)
        self.assertTrue(response.context['post'].image)
        self.assertTrue(response.context['comments'])

    def test_create_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Шаблон изменения поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_cache(self):
        first_request = self.guest_client.get(reverse('posts:index'))
        post = Post.objects.get(pk=1)
        post.text = 'Проверяем кэш'
        post.save()
        second_request = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(first_request.content, second_request.content)
        cache.clear()
        third_request = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(first_request.content, third_request.content)


class FollowTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create(username='Follower')
        cls.not_follower = User.objects.create(username='Not_follower')
        cls.following = User.objects.create(username='Following')
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.follower)
        cls.authorized_not_follower = Client()
        cls.authorized_not_follower.force_login(cls.not_follower)

    def test_authorized_user_can_follow(self):
        """Авторизованный юзер может подписываться и удалять подписки."""
        self.authorized_follower.get(reverse(
            'posts:profile_follow', args=[self.following.get_username()]))
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower, author=self.following).exists())
        self.authorized_follower.get(reverse(
            'posts:profile_unfollow', args=[self.following.get_username()]))
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower, author=self.following).exists())

    def test_new_post_for_followers(self):
        """Новая запись появляется только у подписчиков."""
        Follow.objects.create(
            user=self.follower, author=self.following
        )
        Post.objects.create(
            text='Здравствуйте, дорогие подписчики!',
            author=self.following
        )
        response = self.authorized_follower.get(reverse('posts:follow_index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, 'Здравствуйте, дорогие подписчики!')
        response = self.authorized_not_follower.get(
            reverse('posts:follow_index'))
        self.assertFalse(response.context['page_obj'])
