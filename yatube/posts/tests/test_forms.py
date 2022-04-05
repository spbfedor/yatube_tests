from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

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

        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(
            self.user
        )

    def test_create_post_form(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 555',
            'group': self.group.pk
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(
                'app_posts:post_create'
            ),
            data=form_data,
            follow=True,
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(
                'app_posts:profile',
                kwargs={
                    'username': 'auth'
                }
            )
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост 555',
                group=self.group.pk
            ).exists()
        )

    def test_post_edit_existing_slug(self):
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текстовый пост',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('app_posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True
        )
        # Убедимся, что запись в базе данных не создалась:
        # сравним количество записей в Post до и после отправки формы
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта response берём словарь 'form',
        # указываем ожидаемую ошибку для поля 'text' этого словаря
        self.assertFormError(
            response,
            'form',
            'text',
            'Длина этого поля должна быть не менее 15 символов'
        )
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, 200)
