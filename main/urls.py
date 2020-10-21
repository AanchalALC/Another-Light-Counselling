from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import PostSiteMap, PostTypeSiteMap
from . import views

sitemaps = {
    'posts': PostSiteMap,
    'types': PostTypeSiteMap
}

urlpatterns = [
 
    path('', views.index, name='index'),
    
    path('about', views.about, name='about'),
    path('about/', views.about, name='about'),

    path('faqs', views.faqs, name='faqs'),
    path('faqs/', views.faqs, name='faqs'),

    path('resources', views.resources, name='resources'),
    path('resources/', views.resources, name='resources'),
 
    # path('post/<slug:slug>', views.post, name='post'),
    # path('posts', views.posts, name='posts'),
    # path('posts/', views.posts, name='posts'),
    # path('posts/page/<int:pageno>', views.posts, name='posts'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
 
]
