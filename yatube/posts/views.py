from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


def get_paginated_page(request, queryset):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.order_by('-pub_date').select_related('author')
    page_obj = get_paginated_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = get_paginated_page(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user).select_related(
        'author').order_by('-id')
    post_counter = post_list.count()
    page_obj = get_paginated_page(request, post_list)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user).exists()
    else:
        following = False
    context = {
        'post_list': post_list,
        'post_counter': post_counter,
        'page_obj': page_obj,
        'author': user,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_counter = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post).order_by('-pub_date')
    context = {
        'post': post,
        'post_counter': post_counter,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {
        'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/update_post.html', {
        'form': form, 'is_edit': True, 'post': post})


@login_required
def add_comment(request, post_id):
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
    post_list = Post.objects.filter(
        author__following__user=request.user).order_by(
            '-pub_date').select_related('author')
    page_obj = get_paginated_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not follow.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and follow.exists():
        follow.delete()
    return redirect('posts:profile', username)
