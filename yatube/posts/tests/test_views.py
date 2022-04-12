from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..views import NAMBER_OF_POSTS

User = get_user_model()


class PostPagesTest(
    TestCase
):
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
            text='Тестовый пост',
        )

    def setUp(
        self
    ):
        self.authorized_client = Client()
        self.authorized_client.force_login(
            self.user
        )

    def test_pages_uses_correct_template(
        self
    ):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse(
                'app_posts:index'
            ): 'posts/index.html',
            (
                reverse(
                    'app_posts:group_list',
                    kwargs={
                        'slug': self.group.slug
                    }
                )
            ): 'posts/group_list.html',
            (
                reverse(
                    'app_posts:profile',
                    kwargs={
                        'username': self.user.username
                    }
                )
            ): 'posts/profile.html',
            (
                reverse(
                    'app_posts:post_detail',
                    kwargs={
                        'post_id': self.post.pk
                    }
                )
            ): 'posts/post_detail.html',
            (
                reverse(
                    'app_posts:post_edit',
                    kwargs={
                        'post_id': self.post.pk
                    }
                )
            ): 'posts/create_post.html',
            (
                reverse(
                    'app_posts:post_create',
                )
            ): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(
                reverse_name=reverse_name
            ):
                response = self.authorized_client.get(
                    reverse_name
                )
                self.assertTemplateUsed(
                    response, template
                )

    def test_index_and_profile_page_show_correct_context(
        self
    ):
        """Шаблон index и profile сформирован с правильным контекстом."""

        def check(address, object):
            response = self.authorized_client.get(
                address
            )
            first_object = response.context[
                object
            ][
                0
            ]
            first_dict = {
                first_object.text: self.post.text,
                first_object.author.username: self.user.username,
                first_object.pk: self.post.pk,
                first_object.group: self.group,
                first_object.title: self.title,
                first_object.description: self.description,
                first_object.slug: self.slug
            }
            for expected, actual in first_dict.items():
                with self.subTest(
                    expected=expected
                ):
                    self.assertEqual(
                        expected, actual
                    )

            check(
                reverse(
                    'app_posts:index'
                ),
                'page_obj'
            )

            check(
                reverse(
                    'app_posts:profile',
                    kwargs={
                        'username': self.user.username
                    }
                ),
                'page_obj'
            )

            check(
                reverse(
                    'app_posts:post_detail',
                    kwargs={
                        'post_id': self.post.pk
                    }
                ),
                'post_list'
            )

    def test_group_list_page_show_correct_context(
        self
    ):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'app_posts:group_list',
                kwargs={
                    'slug': self.group.slug
                }
            )
        )
        resp_dict = {
            response.context[
                'group'
            ].title: self.group.title,
            response.context[
                'group'
            ].slug: self.group.slug,
            response.context[
                'group'
            ].description: self.group.description,
            response.context[
                'group'
            ].pk: self.group.pk
        }
        for expected, actual in resp_dict.items():
            with self.subTest(
                expected=expected
            ):
                self.assertEqual(
                    expected, actual
                )

    def test_post_create_show_correct_context(
        self
    ):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'app_posts:post_create'
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(
                value=value
            ):
                form_field = response.context.get(
                    'form'
                ).fields.get(
                    value
                )

                self.assertIsInstance(
                    form_field,
                    expected
                )

    def test_post_edit_show_correct_context(
        self
    ):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'app_posts:post_edit',
                kwargs={
                    'post_id': self.post.pk
                }
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(
                value=value
            ):
                form_field = response.context.get(
                    'form'
                ).fields.get(
                    value
                )

                self.assertIsInstance(
                    form_field,
                    expected
                )


class GroupViewsTest(TestCase):

    @classmethod
    def setUpClass(
        cls
    ):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='auth',
        )

        cls.post = []
        for number in range(13):
            cls.post.append(
                Post(
                    text=f'Тестовый пост номер {number}',
                    author=cls.user
                )
            )
        Post.objects.bulk_create(cls.post)

    def test_first_page_contains_ten_records(
        self
    ):
        response = self.client.get(
            reverse(
                'app_posts:index'
            )
        )

        self.assertEqual(
            len(
                response.context[
                    'page_obj'
                ]
            ),
            NAMBER_OF_POSTS
        )

    def test_second_page_contains_three_records(
        self
    ):
        response = self.client.get(
            reverse(
                'app_posts:index'
            ) + '?page=2'
        )
        self.assertEqual(
            len(
                response.context[
                    'page_obj'
                ]
            ),
            Post.objects.count() - NAMBER_OF_POSTS
        )
