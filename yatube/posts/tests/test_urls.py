from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст поста',
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.author)

    def test_pages_exists_at_desired_location(self):
        """Страница из pages_url доступна любому пользователю."""
        pages_url = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/TestName/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for address, http_status in pages_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, http_status)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/<post_id>/edit/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, '/posts/1/')

    def test_post_post_edit_url_exists_at_desired_location_author(self):
        """Страница /posts/<post_id>/edit/ доступна автору поста."""
        response = self.authorized_client_1.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница /posts/<post_id>/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/TestName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertTemplateUsed(response, template)

    def test_error_404_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    '''def test_error_403_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTemplateUsed(response, 'core/403.html')

    def test_error_500_page(self):
        self.client.raise_request_exception = False
        response = self.client.get('/')
        self.assertEqual(
            response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR
        )
        self.assertTemplateUsed(response, 'core/500.html')
    '''
