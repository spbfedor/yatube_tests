from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTest(
    TestCase
):
    @classmethod
    def setUpClass(
        cls
    ):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='auth'
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

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(
            self.user
        )

    def test_url_exists_at_desired_location(
        self
    ):
        """Страница / доступна любому пользователю."""
        # Список страниц
        url_names = [
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            '/posts/1/',
        ]

        for url in url_names:
            with self.subTest(
                url=url
            ):
                response = self.guest_client.get(
                    url
                )
                self.assertEqual(
                    response.status_code,
                    200
                )

    def test_page_response_an_error(
        self
    ):
        """Страница /unexisting_page/ возвращает ошибку."""
        response = self.guest_client.get(
            '/unexisting_page/'
        )
        self.assertEqual(
            response.status_code,
            404
        )

    def test_create_url_exists_at_desired_location(
        self
    ):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            '/create/'
        )
        self.assertEqual(
            response.status_code,
            200
        )

    def test_create_url_redirect_anonymous(
        self
    ):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(
            '/create/',
            follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )

    def test_post_edit_url_exists_at_desired_location(
        self
    ):
        """Страница /posts/<int:post_id>/edit/ доступна автору."""
        response = self.authorized_client.get(
            '/posts/1/edit/'
        )
        self.assertEqual(
            response.status_code,
            200
        )

    def test_post_edit_url_redirect_anonymous(
        self
    ):
        """Страница /posts/<int:post_id>/edit/
        перенаправляет анонимного пользователя.
        """
        response = self.guest_client.get(
            '/posts/1/edit/',
            follow=True
            )
        self.assertRedirects(
            response,
            '/auth/login/?next=/posts/1/edit/'
        )

    def test_urls_uses_correct_template(
        self
    ):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',

        }
        for address, template in templates_url_names.items():
            with self.subTest(
                address=address
            ):
                response = self.authorized_client.get(
                    address
                )
                self.assertTemplateUsed(
                    response,
                    template
                )
