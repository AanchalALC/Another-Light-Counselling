import os

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse

from .models import Post, PostType


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def faqs(request):
    return render(request, 'faqs.html')
 
def post(request, slug):
    # FETCH OBJ
    post_obj=Post.objects.get(slug = str(slug))
 
    # HUMAN FRIENDLY DATE
    hfr_date = post_obj.created.strftime('%e %b %Y')
    post_obj.hfr_date = hfr_date
 
    # CREATE CONTEXT
    context = {
        'post': post_obj,
    }
 
    # RETURN
    return render(request, 'post.html', context=context)
 
def posts(request, pageno=1):
    # FETCH ALL POSTS
    # posts = Post.objects.filter(p_type__type_name = typename).exclude(slug='about').order_by('-created', 'title')
    posts = Post.objects.all().order_by('-created', 'title')
 
    # PAGINATE
    paginator = Paginator(posts, 10)
    page_num = int(pageno)
    page_obj = paginator.get_page(page_num)
    posts = page_obj.object_list
 
    # HUMAN FRIENDLY DATE
    for post in posts:
        hfr_date = post.created.strftime('%e %b %Y')
        post.hfr_date = hfr_date
 
        post.preview = str(post.content).split('</p>')[0].split('<p>')[1]
 
    # SET CONTEXT
    context = {
        'posts': posts,
        'pageinator': paginator,
        'page_obj': page_obj,
    }
 
    # RETURN
    return render(request, 'posts.html', context=context)
