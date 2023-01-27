from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст более 15 символов',
            author=cls.user
        )

    def test_groups_have_correct_object_name(self):
        group = self.group
        self.assertEqual(group.title, str(group))

    def test_posts_have_correct_object_name(self):
        post = self.post
        self.assertEqual(post.text[:15], str(post))

    def test_verbose_post_model(self):
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_post_model(self):
        post = self.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
