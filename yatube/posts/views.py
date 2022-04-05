from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

NAMBER_OF_POSTS = 10


def index(
    request
):
    post_list = Post.objects.select_related(
        'group'
    ).all()
    paginator = Paginator(
        post_list,
        NAMBER_OF_POSTS
    )
    page_number = request.GET.get(
        "page"
    )
    page_obj = paginator.get_page(
        page_number
    )
    template = "posts/index.html"
    title = "Последние обновления на сайте"
    context = {
        "page_obj": page_obj,
        "title": title,
    }
    return render(
        request,
        template,
        context
    )


def group_posts(
    request,
    slug
):
    template = "posts/group_list.html"
    group = get_object_or_404(
        Group,
        slug=slug
    )
    post_list = group.posts.order_by(
        "-pub_date"
    )
    paginator = Paginator(
        post_list,
        NAMBER_OF_POSTS
    )
    page_number = request.GET.get(
        "page"
    )
    page_obj = paginator.get_page(
        page_number
    )
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(
        request,
        template,
        context
    )


def profile(
    request,
    username
):
    author = get_object_or_404(
        User,
        username=username
    )
    post_list = Post.objects.filter(
        author=author.id
    ).order_by(
        "-pub_date"
    )
    paginator = Paginator(
        post_list,
        NAMBER_OF_POSTS
    )
    page_number = request.GET.get(
        "page"
    )
    page_obj = paginator.get_page(
        page_number
    )
    template = "posts/profile.html"
    count = post_list.count()
    context = {
        "post_list": post_list,
        "author": author,
        "page_obj": page_obj,
        "count": count,
    }
    return render(
        request,
        template,
        context
    )


def post_detail(
    request,
    post_id
):
    one_post = get_object_or_404(
        Post,
        pk=post_id
    )
    post_list = Post.objects.filter(
        pk=post_id
    )
    count = one_post.author.posts.count()
    template = "posts/post_detail.html"
    context = {
        'one_post': one_post,
        'count': count,
        'post_list': post_list
    }
    return render(
        request,
        template,
        context
    )


@login_required
def post_create(
    request
):
    form = PostForm(
        request.POST or None
    )

    if form.is_valid():
        post = form.save(
            commit=False
        )
        post.author = request.user
        post.save()
        return redirect(
            "app_posts:profile",
            username=post.author
        )
    return render(
        request,
        "posts/create_post.html",
        {
            "form": form
        }
    )


@login_required
def post_edit(
    request,
    post_id
):
    post = get_object_or_404(
        Post,
        pk=post_id
    )
    form = PostForm(
        request.POST or None,
        instance=post
    )
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect(
                "app_posts:post_detail",
                post_id
            )
        context = {
            'form': form,
            'is_edit': True,
            'post': post
        }
        return render(
            request,
            "posts/create_post.html",
            context
        )
    return redirect(
        "app_posts:post_detail",
        post_id
    )
