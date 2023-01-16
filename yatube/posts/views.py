from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from . forms import PostForm

AMOUNT_POST = 10


def index(request):
    title = "Последние обновления на сайте"
    posts = Post.objects.all()
    page_obj = get_page_paginator(request, posts)
    context = {
        'title': title,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_paginator(request, posts)
    context = {'group': group,
               'posts': posts,
               'page_obj': page_obj}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = get_page_paginator(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_title = post.text[:30]
    author = post.author
    author_posts = author.posts.all().count()
    context = {
        "post": post,
        "post_title": post_title,
        "author": author,
        "author_posts": author_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    groups = Group.objects.all()
    return render(
        request,
        "posts/create_post.html",
        {'form': form, "groups": groups}
    )

    
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()
    form = PostForm(request.POST or None, instance=post)
    context = {
        "form": form,
        "is_edit": True,
        "post": post,
        "groups": groups,
    }
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    return render(request, "posts/create_post.html", context)


def get_page_paginator(request, posts):
    pagi = Paginator(posts, AMOUNT_POST)
    page_number = request.GET.get('page')
    page_obj = pagi.get_page(page_number)
    return page_obj
