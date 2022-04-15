import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
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
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст поста',
            image=cls.uploaded,
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='TestName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{self.user}'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_profile_group_page_show_correct_context(self):
        """Шаблоны correct_context сформированы с правильным контекстом."""
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': f'{self.author}'}),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
        ]
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                object = response.context['page_obj'][0]
                test_text = object.text
                test_author = object.author
                test_group = object.group
                test_image = object.image
                self.assertEqual(test_text, 'Тестовый текст поста')
                self.assertEqual(test_author.username, 'author')
                self.assertEqual(test_group.title, 'Тестовый заголовок')
                self.assertEqual(test_image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        first_object = response.context['post']
        test_text_0 = first_object.text
        test_author_0 = first_object.author
        test_image_0 = first_object.image
        self.assertEqual(test_text_0, 'Тестовый текст поста')
        self.assertEqual(test_author_0.username, 'author')
        self.assertEqual(test_image_0, self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client_1.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_authorized_user_can_follow_profile(self):
        '''Тест. Авторизованный пользователь может подписываться на
        других пользователей.'''
        follow_count = Follow.objects.count()
        follow = Follow.objects.create(
            user=self.user,
            author=self.author
        )
        follow.save()
        response = Follow.objects.count()
        self.assertEqual(response, follow_count + 1)

    def test_authorized_user_can_unfollow_profile(self):
        '''Тест. Авторизованный пользователь может отписываться от
        других пользователей.'''
        follow_count = Follow.objects.count()
        follow = Follow.objects.create(
            user=self.user,
            author=self.author
        )
        follow.delete()
        response = Follow.objects.count()
        self.assertEqual(response, follow_count)
