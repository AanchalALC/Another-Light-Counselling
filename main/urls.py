from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import PostSiteMap, PostTypeSiteMap, StaticSiteMap
from . import views

sitemaps = {
    'static': StaticSiteMap,
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

    path('reviews', views.reviews, name='reviews'),
    path('reviews/', views.reviews, name='reviews'),

    path('contact', views.contact, name='contact'),
    path('contact/', views.contact, name='contact'),
 
    path('post/<slug:slug>', views.post, name='post'),
    path('blog', views.blog, name='blog'),
    path('blog/', views.blog, name='blog'),
    path('blog/page/<int:pageno>', views.blog, name='blog'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
 
]
