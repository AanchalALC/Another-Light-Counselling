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

    path('psychological-counselling-therapy', views.psychologicalCounsellingTherapy, name='psychological-counselling-therapy'),
    path('psychological-counselling-therapy/', views.psychologicalCounsellingTherapy, name='psychological-counselling-therapy'),
    path('psychological-counselling-therapy-thankyou', views.pctThankYou, name='psychological-counselling-therapy-thankyou'),
    path('psychological-counselling-therapy-thankyou/', views.pctThankYou, name='psychological-counselling-therapy-thankyou'),

    path('about', views.about, name='about'),
    path('about/', views.about, name='about'),
    path('about/another-light', views.about, name='about'),
    path('about/another-light/', views.about, name='about'),

    path('faqs', views.faqs, name='faqs'),
    path('faqs/', views.faqs, name='faqs'),
    path('faqs/another-light', views.faqs, name='faqs'),
    path('faqs/another-light/', views.faqs, name='faqs'),

    path('resources', views.resources, name='resources'),
    path('resources/', views.resources, name='resources'),

    path('reviews', views.reviews, name='reviews'),
    path('reviews/', views.reviews, name='reviews'),

    path('contact', views.contact, name='contact'),
    path('contact/', views.contact, name='contact'),

    path('policy/<slug:slug>', views.policy, name='policy'),
    path('committee/<slug:slug>', views.committee, name='committee'),

    path('services', views.services, name='services'),
    path('services/', views.services, name='services'),
    path('service/<slug:slug>', views.service, name='service'),

    path('doifeels', views.doifeels, name='doifeels'),
    path('doifeels/', views.doifeels, name='doifeels'),
    path('doifeel/<slug:slug>', views.doifeel, name='doifeel'), 
    
    path('howtofeels', views.howtofeels, name='howtofeels'),
    path('howtofeels/', views.howtofeels, name='howtofeels'),
    path('howtofeel/<slug:slug>', views.howtofeel, name='howtofeel'), 
 
    path('post/<slug:slug>', views.post, name='post'),
    path('blog', views.blog, name='blog'),
    path('blog/', views.blog, name='blog'),
    path('blog/page/<int:pageno>', views.blog, name='blog'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
 
]
