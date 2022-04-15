from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow, User
from .utils import paginator_mod


def index(request):
    '''Главная страница сайта'''
    page_obj = paginator_mod(Post.objects.all(), request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''Страница с группированными постами'''
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginator_mod(Post.objects.filter(group=group), request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''Страница всех постов пользователя'''
    author = get_object_or_404(User, username=username)
    page_obj = paginator_mod(Post.objects.filter(author=author), request)
    following = request.user.is_authenticated and Follow.objects.filter(
        user__username=request.user, author=author).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''Страница с информацией о посте'''
    post = get_object_or_404(Post, pk=post_id)
    group = post.group
    author = post.author
    count_posts = author.posts.count
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'group': group,
        'author': author,
        'comments': comments,
        'count_posts': count_posts,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''Страница создания нового поста'''
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    '''Страница редактирования поста'''
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post': post}
                  )


@login_required
def add_comment(request, post_id):
    '''Оставить комментарий'''
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    '''Страница подписки на автора'''
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    page_obj = paginator_mod(posts, request)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    '''Подписаться на автора'''
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user=request.user, author=author).exists()
    if request.user != author and not following:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    '''Отписаться от автора'''
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    follow.delete()
    return redirect('posts:profile', username=username)
