from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import PostSiteMap, PostTypeSiteMap, StaticSiteMap
from . import views
from django.urls import re_path

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

    path('faqs', views.faqs, name='faqs'),
    path('faqs/', views.faqs, name='faqs'),

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

    path('careers', views.careers, name='careers'),
    path('careers/', views.careers, name='careers'),
    path('jd/<slug:slug>', views.jd, name='jd'),

    path('post/<slug:slug>', views.post, name='post'),
    path('blog', views.blog, name='blog'),
    path('blog/', views.blog, name='blog'),
    path('blog/page/<int:pageno>', views.blog, name='blog'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # You can keep these if you still want /team as a list page
    path('team', views.team_list, name='team'),
    path('team/', views.team_list, name='team'),

    # Profile detail should now live under /about/<slug>
    path('about/<slug:slug>', views.member_profile, name='member-profile'),
    path('about/<slug:slug>/', views.member_profile, name='member-profile'),

    re_path(r"^aanchal-onboarding-plan/?$", views.onboarding_plan, name="onboarding_plan"),
]
