from django import forms

from .models import Post, Comment, Follow


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Введите текст',
            'group': 'Выберете группу',
            'image': 'Загрузите картинку',
        }
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Введите комментарий',
        }
        labels = {
            'text': 'Текст комментария',
        }


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ('user', 'author',)
        help_texts = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        labels = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
