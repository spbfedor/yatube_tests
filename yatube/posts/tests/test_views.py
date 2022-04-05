from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

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
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(
            self.user
        )

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(
        self
    ):
        """URL-адрес использует соответствующий шаблон."""

        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse(
                'app_posts:index'
            ): 'posts/index.html',
            (
                reverse(
                    'app_posts:group_list',
                    kwargs={
                        'slug': 'test-slug'
                    }
                )
            ): 'posts/group_list.html',
            (
                reverse(
                    'app_posts:profile',
                    kwargs={
                        'username': 'auth'
                    }
                )
            ): 'posts/profile.html',
            (
                reverse(
                    'app_posts:post_detail',
                    kwargs={
                        'post_id': 1
                    }
                )
            ): 'posts/post_detail.html',
            (
                reverse(
                    'app_posts:post_edit',
                    kwargs={
                        'post_id': 1
                    }
                )
            ): 'posts/create_post.html',
            (
                reverse(
                    'app_posts:post_create',
                )
            ): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
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

    def test_index_page_show_correct_context(
        self
    ):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'app_posts:index'
            )
        )
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author.username
        self.assertEqual(
            posts_text_0,
            'Тестовый пост'
        )
        self.assertEqual(
            posts_author_0,
            'auth'
        )

    def test_group_list_page_show_correct_context(
        self
    ):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'app_posts:group_list',
                kwargs={
                    'slug': 'test-slug'
                }
            )
        )
        self.assertEqual(
            response.context[
                'group'
            ].title,
            'Тестовая группа'
        )
        self.assertEqual(
            response.context[
                'group'
            ].slug,
            'test-slug'
        )
        self.assertEqual(
            response.context[
                'group'
            ].description,
            'Тестовое описание'
        )

    def test_profile_page_show_correct_context(
        self
    ):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'app_posts:profile',
                kwargs={
                    'username': 'auth'
                }
            )
        )
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author.username
        self.assertEqual(
            posts_text_0,
            'Тестовый пост'
        )
        self.assertEqual(
            posts_author_0,
            'auth'
        )

    def test_detail_page_show_correct_context(
        self
    ):
        """Шаблон detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'app_posts:post_detail',
                kwargs={
                    'post_id': 1
                }
            )
        )
        first_object = response.context['post_list'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author.username
        posts_post_id_0 = first_object.pk
        self.assertEqual(
            posts_text_0,
            'Тестовый пост'
        )
        self.assertEqual(
            posts_author_0,
            'auth'
        )
        self.assertEqual(
            posts_post_id_0,
            1
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
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(
                value=value
            ):
                form_field = response.context.get(
                    'form'
                ).fields.get(
                    value
                )
                # Проверяет, что поле формы является экземпляром
                # указанного класса
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
                    'post_id': 1
                }
            )
        )
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(
                value=value
            ):
                form_field = response.context.get(
                    'form'
                ).fields.get(
                    value
                )
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(
                    form_field,
                    expected
                )


class GroupViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.

    @classmethod
    def setUpClass(
        cls
    ):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='auth',
        )

        cls.post_1 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1',
        )

        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 2'
        )

        cls.post_3 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 3'
        )

        cls.post_4 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 4'
        )

        cls.post_5 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 5'
        )

        cls.post_6 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 6'
        )

        cls.post_7 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 7'
        )

        cls.post_8 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 8'
        )

        cls.post_9 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 9'
        )

        cls.post_10 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 10'
        )

        cls.post_11 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 11'
        )

        cls.post_12 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 12'
        )

        cls.post_13 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 13'
        )

    def test_first_page_contains_ten_records(
        self
    ):
        response = self.client.get(
            reverse(
                'app_posts:index'
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(
                response.context[
                    'page_obj'
                ]
            ),
            10
        )

    def test_second_page_contains_three_records(
        self
    ):
        # Проверка: на второй странице должно быть три поста.
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
            3
        )
