from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostForm(TestCase):
    @classmethod
    def setUpClass(
        cls
    ):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='auth',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 555',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(
            self.user
        )

    def test_create_post_form(self):
        """Валидная форма создает запись в Post."""

        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
        }

        response = self.authorized_client.post(
            reverse(
                'app_posts:post_create'
            ),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse(
                'app_posts:profile',
                kwargs={
                    'username': self.user.username
                }
            )
        )

        self.assertEqual(
            Post.objects.count(),
            posts_count + 1
        )

        edited_post = Post.objects.get(pk=self.post.pk)

        self.assertEqual(
            edited_post.text,
            form_data['text']
        )

    def test_post_edit_existing_slug(
        self
    ):

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'app_posts:post_edit',
                args=(
                    self.post.pk,
                )
            ),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            Post.objects.count(),
            posts_count
        )

        self.assertFormError(
            response,
            'form',
            'text',
            'Длина этого поля должна быть не менее 15 символов'
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )

    def test_for_updatinga_record_in_the_database(self):
        """Форма перезаписывает запись в БД"""

        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
        }
        self.authorized_client.post(
            reverse(
                'app_posts:post_edit',
                args=(
                    self.post.pk,
                )
            ),
            data=form_data,
            follow=True
        )

        edited_post = Post.objects.get(pk=self.post.pk)

        self.assertEqual(
            edited_post.text,
            form_data['text']
        )
