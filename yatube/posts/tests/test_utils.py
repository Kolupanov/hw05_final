from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = []
        for i in range(0, 13):
            cls.posts.append(Post.objects.create(
                author=cls.author,
                group=cls.group,
                text=f'Тестовый текст поста {i}',)
            )
        cls.reverse_names = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'author'}),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
        ]

    def test_first_page_contains_ten_records(self):
        """Тест. Количество постов на первой странице равно 10."""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Тест. На второй странице должно быть три поста."""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
