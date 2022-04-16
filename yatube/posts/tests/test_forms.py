import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок 2',
            slug='test-slug_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст поста',
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
        cls.guest_client = Client()
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.author)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_forms_post_create(self):
        '''Тест forms создания поста.'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client_1.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст поста',
            group=1,
            image='posts/small.gif').exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_cant_create_post(self):
        '''Тест. Неавторизованный пользователь не может создать пост'''
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data={},
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_forms_post_edit(self):
        '''Тест forms редактирования поста.'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый отредактированный текст',
            'group': self.group.id,
        }
        response = self.authorized_client_1.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text='Тестовый отредактированный текст',
            group=1).exists()
        )

        form_data_2 = {
            'text': 'Тестовый отредактированный текст',
            'group': self.group_2.id,
        }
        response_2 = self.authorized_client_1.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data_2,
            follow=True
        )
        self.assertRedirects(response_2, reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertTrue(Post.objects.filter(
            text='Тестовый отредактированный текст',
            group=2).exists()
        )

    def test_forms_add_comment(self):
        '''Тест forms отправки комментария.'''
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client_1.post(reverse(
            'posts:add_comment', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Тестовый комментарий').exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_cant_create_comment(self):
        '''Тест. Неавторизованный пользователь не может
        оставить комментарий.'''
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_cash_index_page(self):
        '''Тест. Кеширование на главной странице.'''
        response = self.authorized_client_1.get(reverse('posts:index'))
        first_object = response.content
        form_data = {
            'text': 'Тестовый текст поста',
            'group': self.group.id,
        }
        post_create = self.authorized_client_1.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(post_create, reverse(
            'posts:profile', kwargs={'username': self.author.username})
        )
        response_2 = self.authorized_client_1.get(reverse('posts:index'))
        second_object = response_2.content
        self.assertEqual(first_object, second_object)
        cache.clear()
        response_after_cache_clear = self.authorized_client_1.get(
            reverse('posts:index')
        )
        self.assertNotEqual(response_2, response_after_cache_clear)

    def test_label(self):
        '''Тест поля label.'''
        fields_label = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, value in fields_label.items():
            with self.subTest(field=field):
                self.assertEqual(
                    CreateFormTests.form.fields[field].label, value)

    def test_help_text(self):
        '''Тест поля help_text.'''
        fields_help_text = {
            'text': 'Введите текст',
            'group': 'Выберете группу',
            'image': 'Загрузите картинку',
        }
        for field, value in fields_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    CreateFormTests.form.fields[field].help_text, value)
